"""
Food Scan Service
AI-powered food recognition and nutrition analysis
"""
import base64
import time
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.core.config import settings
from app.models.food_scan import FoodScan, FoodScanResult, ScanStatus, ScanType
from app.models.nutrition import FoodEntry, NutritionLog, MealType, FoodSource
from app.schemas.food_scan import FoodScanCreate, FoodScanResponse, AIFoodAnalysis

logger = get_logger(__name__)

# Mock food database for demonstration
# In production, use a proper food database API or ML model
COMMON_FOODS = {
    "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3, "weight": 180},
    "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4, "weight": 118},
    "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "weight": 100},
    "rice": {"calories": 206, "protein": 4.3, "carbs": 45, "fat": 0.4, "weight": 158},
    "salad": {"calories": 20, "protein": 1.5, "carbs": 3.5, "fat": 0.2, "weight": 100},
    "pizza": {"calories": 285, "protein": 12, "carbs": 36, "fat": 10, "weight": 107},
    "burger": {"calories": 354, "protein": 20, "carbs": 29, "fat": 17, "weight": 150},
    "pasta": {"calories": 220, "protein": 8, "carbs": 43, "fat": 1.3, "weight": 140},
    "sandwich": {"calories": 252, "protein": 9, "carbs": 34, "fat": 9, "weight": 100},
    "eggs": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "weight": 100},
}


class FoodScanService:
    """Food scanning and AI analysis service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def scan_food_image(
        self,
        user_id: int,
        image_base64: str,
        estimate_portion: bool = True
    ) -> FoodScan:
        """
        Analyze food image using AI
        Returns scan with detected foods and nutrition estimates
        """
        start_time = time.time()
        
        # Create scan record
        scan = FoodScan(
            user_id=user_id,
            scan_type=ScanType.PHOTO,
            status=ScanStatus.PROCESSING,
            image_base64=image_base64[:100] + "...",  # Store truncated for reference
            scanned_at=datetime.utcnow()
        )
        
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        
        try:
            # Analyze with AI (mock implementation)
            analysis = await self._analyze_food_image(image_base64)
            
            # Create results for each detected food
            for food_data in analysis.get("foods_detected", []):
                result = FoodScanResult(
                    scan_id=scan.id,
                    food_name=food_data.get("name", "Unknown Food"),
                    confidence=food_data.get("confidence", 0.5),
                    estimated_portion=food_data.get("portion", "1 serving"),
                    estimated_weight_g=food_data.get("weight_g", 100),
                    estimated_calories=food_data.get("calories", 0),
                    estimated_protein_g=food_data.get("protein_g", 0),
                    estimated_carbs_g=food_data.get("carbs_g", 0),
                    estimated_fat_g=food_data.get("fat_g", 0),
                    nutrition_data=food_data.get("full_nutrition"),
                    alternative_matches=food_data.get("alternatives", [])
                )
                self.db.add(result)
            
            # Update scan status
            scan.status = ScanStatus.COMPLETED
            scan.processed_at = datetime.utcnow()
            scan.processing_time_ms = int((time.time() - start_time) * 1000)
            scan.confidence_score = analysis.get("overall_confidence", 0.7)
            scan.model_used = "gpt-4-vision-preview"
            scan.raw_response = analysis
            
            self.db.commit()
            self.db.refresh(scan)
            
            logger.info(f"Food scan completed for user {user_id}, found {len(analysis.get('foods_detected', []))} items")
            
        except Exception as e:
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            self.db.commit()
            
            logger.error(f"Food scan failed for user {user_id}: {e}", exc_info=True)
        
        return scan
    
    async def scan_barcode(
        self,
        user_id: int,
        barcode: str
    ) -> FoodScan:
        """
        Look up food by barcode
        """
        start_time = time.time()
        
        scan = FoodScan(
            user_id=user_id,
            scan_type=ScanType.BARCODE,
            status=ScanStatus.PROCESSING,
            barcode=barcode,
            scanned_at=datetime.utcnow()
        )
        
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        
        try:
            # Look up barcode in database
            food_entry = self.db.query(FoodEntry).filter(
                FoodEntry.barcode == barcode
            ).first()
            
            if food_entry:
                result = FoodScanResult(
                    scan_id=scan.id,
                    food_name=food_entry.name,
                    brand=food_entry.brand,
                    confidence=1.0,
                    estimated_weight_g=food_entry.serving_size,
                    estimated_calories=food_entry.calories,
                    estimated_protein_g=food_entry.protein_g,
                    estimated_carbs_g=food_entry.carbohydrates_g,
                    estimated_fat_g=food_entry.fat_g,
                    matched_food_entry_id=food_entry.id,
                    match_confidence=1.0
                )
                self.db.add(result)
                scan.status = ScanStatus.COMPLETED
                scan.confidence_score = 1.0
            else:
                # Try external API lookup (mock)
                food_data = await self._lookup_barcode_external(barcode)
                
                if food_data:
                    result = FoodScanResult(
                        scan_id=scan.id,
                        food_name=food_data.get("name", "Unknown Product"),
                        brand=food_data.get("brand"),
                        confidence=0.9,
                        estimated_calories=food_data.get("calories", 0),
                        estimated_protein_g=food_data.get("protein_g", 0),
                        estimated_carbs_g=food_data.get("carbs_g", 0),
                        estimated_fat_g=food_data.get("fat_g", 0)
                    )
                    self.db.add(result)
                    scan.status = ScanStatus.COMPLETED
                else:
                    scan.status = ScanStatus.FAILED
                    scan.error_message = "Barcode not found"
            
            scan.processed_at = datetime.utcnow()
            scan.processing_time_ms = int((time.time() - start_time) * 1000)
            
            self.db.commit()
            self.db.refresh(scan)
            
        except Exception as e:
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            self.db.commit()
            logger.error(f"Barcode scan failed: {e}", exc_info=True)
        
        return scan
    
    def get_scan(self, scan_id: int, user_id: int) -> Optional[FoodScan]:
        """Get specific scan"""
        return self.db.query(FoodScan).filter(
            FoodScan.id == scan_id,
            FoodScan.user_id == user_id
        ).first()
    
    def get_user_scans(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[FoodScan]:
        """Get user's scan history"""
        return self.db.query(FoodScan).filter(
            FoodScan.user_id == user_id
        ).order_by(FoodScan.scanned_at.desc()).offset(offset).limit(limit).all()
    
    def confirm_scan_result(
        self,
        user_id: int,
        result_id: int,
        meal_type: MealType,
        quantity: float = 1,
        serving_size: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Optional[NutritionLog]:
        """Confirm scan result and add to nutrition log"""
        result = self.db.query(FoodScanResult).filter(
            FoodScanResult.id == result_id
        ).first()
        
        if not result:
            return None
        
        # Verify ownership through scan
        scan = self.db.query(FoodScan).filter(
            FoodScan.id == result.scan_id,
            FoodScan.user_id == user_id
        ).first()
        
        if not scan:
            return None
        
        # Calculate nutrition based on quantity
        weight = serving_size or result.estimated_weight_g or 100
        multiplier = quantity
        
        log = NutritionLog(
            user_id=user_id,
            food_entry_id=result.matched_food_entry_id,
            log_date=scan.scanned_at.date(),
            meal_type=meal_type,
            food_name=result.user_selected_name or result.food_name,
            brand=result.brand,
            quantity=quantity,
            serving_size=weight,
            serving_unit="g",
            calories=(result.estimated_calories or 0) * multiplier,
            protein_g=(result.estimated_protein_g or 0) * multiplier,
            carbohydrates_g=(result.estimated_carbs_g or 0) * multiplier,
            fat_g=(result.estimated_fat_g or 0) * multiplier,
            fiber_g=0,
            sugar_g=0,
            source=FoodSource.SCAN,
            food_scan_id=scan.id,
            notes=notes
        )
        
        self.db.add(log)
        
        # Mark result as added
        result.added_to_log = True
        result.nutrition_log_id = log.id
        
        # Mark scan as confirmed
        scan.user_confirmed = True
        
        self.db.commit()
        self.db.refresh(log)
        
        logger.info(f"Scan result {result_id} added to nutrition log for user {user_id}")
        return log
    
    async def _analyze_food_image(self, image_base64: str) -> dict:
        """
        Analyze food image using AI
        Mock implementation - in production, use OpenAI Vision API or custom ML model
        """
        # This is a mock implementation
        # In production, integrate with OpenAI GPT-4 Vision API
        
        if settings.OPENAI_API_KEY:
            # Real implementation would go here
            # response = await openai.ChatCompletion.create(...)
            pass
        
        # Mock response
        import random
        foods = list(COMMON_FOODS.keys())
        detected_food = random.choice(foods)
        food_data = COMMON_FOODS[detected_food]
        
        return {
            "foods_detected": [
                {
                    "name": detected_food.title(),
                    "confidence": round(random.uniform(0.7, 0.95), 2),
                    "portion": "1 serving",
                    "weight_g": food_data["weight"],
                    "calories": food_data["calories"],
                    "protein_g": food_data["protein"],
                    "carbs_g": food_data["carbs"],
                    "fat_g": food_data["fat"],
                    "alternatives": [
                        {"name": random.choice(foods).title(), "confidence": 0.3}
                    ]
                }
            ],
            "overall_confidence": round(random.uniform(0.75, 0.9), 2),
            "analysis_notes": "Food detected successfully"
        }
    
    async def _lookup_barcode_external(self, barcode: str) -> Optional[dict]:
        """
        Look up barcode in external database
        Mock implementation
        """
        # In production, integrate with Open Food Facts API or similar
        # https://world.openfoodfacts.org/api/v0/product/{barcode}.json
        
        return None  # Return None to simulate "not found"
