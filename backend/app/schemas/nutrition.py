"""
Nutrition Pydantic Schemas
Request/Response models for nutrition tracking
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.nutrition import MealType, FoodSource


# ============ Food Entry Schemas ============

class FoodEntryBase(BaseModel):
    """Base food entry schema"""
    name: str = Field(..., max_length=255)
    brand: Optional[str] = None
    barcode: Optional[str] = None
    serving_size: float = 100
    serving_unit: str = "g"
    calories: float = 0
    protein_g: float = 0
    carbohydrates_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0
    sugar_g: float = 0


class FoodEntryCreate(FoodEntryBase):
    """Create food entry"""
    saturated_fat_g: Optional[float] = None
    trans_fat_g: Optional[float] = None
    cholesterol_mg: Optional[float] = None
    sodium_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class FoodEntryUpdate(BaseModel):
    """Update food entry"""
    name: Optional[str] = None
    brand: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    category: Optional[str] = None


class FoodEntryResponse(FoodEntryBase):
    """Food entry response"""
    id: int
    saturated_fat_g: Optional[float] = None
    cholesterol_mg: Optional[float] = None
    sodium_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class FoodSearch(BaseModel):
    """Food search request"""
    query: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    limit: int = Field(default=20, le=50)


# ============ Nutrition Log Schemas ============

class NutritionLogCreate(BaseModel):
    """Create nutrition log entry"""
    food_entry_id: Optional[int] = None
    log_date: date
    meal_type: MealType
    food_name: str = Field(..., max_length=255)
    brand: Optional[str] = None
    quantity: float = 1
    serving_size: float
    serving_unit: str
    calories: float
    protein_g: float = 0
    carbohydrates_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0
    sugar_g: float = 0
    sodium_mg: Optional[float] = None
    source: FoodSource = FoodSource.MANUAL
    notes: Optional[str] = None


class NutritionLogUpdate(BaseModel):
    """Update nutrition log entry"""
    meal_type: Optional[MealType] = None
    quantity: Optional[float] = None
    serving_size: Optional[float] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    notes: Optional[str] = None


class NutritionLogResponse(BaseModel):
    """Nutrition log response"""
    id: int
    user_id: int
    food_entry_id: Optional[int] = None
    log_date: date
    log_time: datetime
    meal_type: MealType
    food_name: str
    brand: Optional[str] = None
    quantity: float
    serving_size: float
    serving_unit: str
    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: Optional[float] = None
    source: FoodSource
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuickAddCalories(BaseModel):
    """Quick add calories without full food details"""
    log_date: date
    meal_type: MealType
    calories: float = Field(..., gt=0)
    name: str = "Quick Add"
    notes: Optional[str] = None


# ============ Daily Summary Schemas ============

class MealSummary(BaseModel):
    """Summary for a single meal"""
    meal_type: MealType
    total_calories: float = 0
    total_protein_g: float = 0
    total_carbs_g: float = 0
    total_fat_g: float = 0
    items_count: int = 0
    items: List[NutritionLogResponse] = []


class DailySummaryResponse(BaseModel):
    """Daily nutrition summary"""
    date: date
    total_calories: float = 0
    calorie_goal: Optional[int] = None
    calories_remaining: float = 0
    calorie_goal_percent: float = 0
    
    total_protein_g: float = 0
    protein_goal_g: Optional[int] = None
    protein_goal_percent: float = 0
    
    total_carbs_g: float = 0
    carbs_goal_g: Optional[int] = None
    carbs_goal_percent: float = 0
    
    total_fat_g: float = 0
    fat_goal_g: Optional[int] = None
    fat_goal_percent: float = 0
    
    total_fiber_g: float = 0
    total_sugar_g: float = 0
    total_sodium_mg: float = 0
    
    meals: List[MealSummary] = []
    total_items: int = 0


class WeeklySummaryResponse(BaseModel):
    """Weekly nutrition summary"""
    start_date: date
    end_date: date
    daily_summaries: List[DailySummaryResponse] = []
    
    # Averages
    avg_calories: float = 0
    avg_protein_g: float = 0
    avg_carbs_g: float = 0
    avg_fat_g: float = 0
    
    # Totals
    total_calories: float = 0
    days_logged: int = 0
    days_on_goal: int = 0


class MacroBreakdown(BaseModel):
    """Macronutrient breakdown"""
    protein_g: float = 0
    protein_calories: float = 0
    protein_percent: float = 0
    
    carbs_g: float = 0
    carbs_calories: float = 0
    carbs_percent: float = 0
    
    fat_g: float = 0
    fat_calories: float = 0
    fat_percent: float = 0
    
    total_calories: float = 0
