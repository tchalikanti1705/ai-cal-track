"""
Food Scan Pydantic Schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.food_scan import ScanStatus, ScanType


# ============ Food Scan Request Schemas ============

class FoodScanCreate(BaseModel):
    """Create food scan request"""
    scan_type: ScanType = ScanType.PHOTO
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None


class FoodScanFromImage(BaseModel):
    """Scan food from image"""
    image_base64: str = Field(..., description="Base64 encoded image")
    estimate_portion: bool = True


class FoodScanFromBarcode(BaseModel):
    """Scan food from barcode"""
    barcode: str = Field(..., min_length=8, max_length=20)


# ============ Food Scan Result Schemas ============

class FoodScanResultResponse(BaseModel):
    """Single detected food item"""
    id: int
    food_name: str
    brand: Optional[str] = None
    confidence: float
    estimated_portion: Optional[str] = None
    estimated_weight_g: Optional[float] = None
    estimated_calories: Optional[float] = None
    estimated_protein_g: Optional[float] = None
    estimated_carbs_g: Optional[float] = None
    estimated_fat_g: Optional[float] = None
    alternative_matches: Optional[List[dict]] = None
    added_to_log: bool = False
    
    class Config:
        from_attributes = True


class FoodScanResponse(BaseModel):
    """Food scan response"""
    id: int
    user_id: int
    scan_type: ScanType
    status: ScanStatus
    scanned_at: datetime
    processed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    results: List[FoodScanResultResponse] = []
    
    class Config:
        from_attributes = True


# ============ Scan Confirmation Schemas ============

class ScanResultConfirm(BaseModel):
    """Confirm and add scan result to log"""
    result_id: int
    meal_type: str
    quantity: float = 1
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    use_custom_name: Optional[str] = None
    notes: Optional[str] = None


class ScanResultCorrect(BaseModel):
    """Correct scan result with user's input"""
    result_id: int
    corrected_name: str
    corrected_portion: Optional[str] = None
    corrected_weight_g: Optional[float] = None
    corrected_calories: Optional[float] = None


# ============ AI Analysis Response ============

class AIFoodAnalysis(BaseModel):
    """AI food analysis result"""
    foods_detected: List[dict] = []
    total_estimated_calories: float = 0
    confidence_level: str = "medium"
    analysis_notes: Optional[str] = None
    suggestions: List[str] = []
