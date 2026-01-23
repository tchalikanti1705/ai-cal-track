"""
Nutrition Models - Food entries, nutrition logs, and daily summaries
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, 
    ForeignKey, Text, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class MealType(enum.Enum):
    BREAKFAST = "breakfast"
    MORNING_SNACK = "morning_snack"
    LUNCH = "lunch"
    AFTERNOON_SNACK = "afternoon_snack"
    DINNER = "dinner"
    EVENING_SNACK = "evening_snack"


class FoodSource(enum.Enum):
    MANUAL = "manual"          # User manually entered
    SCAN = "scan"              # AI food scan
    BARCODE = "barcode"        # Barcode scan
    DATABASE = "database"      # Selected from food database
    RECIPE = "recipe"          # From saved recipe
    QUICK_ADD = "quick_add"    # Quick calorie add


class FoodEntry(BaseModel):
    """
    Individual food items in the database
    Acts as a food reference library
    """
    __tablename__ = "food_entries"
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    barcode = Column(String(50), nullable=True, index=True)
    
    # Serving information
    serving_size = Column(Float, nullable=False, default=100)
    serving_unit = Column(String(50), nullable=False, default="g")
    servings_per_container = Column(Float, nullable=True)
    
    # Macronutrients (per serving)
    calories = Column(Float, nullable=False, default=0)
    protein_g = Column(Float, nullable=False, default=0)
    carbohydrates_g = Column(Float, nullable=False, default=0)
    fat_g = Column(Float, nullable=False, default=0)
    fiber_g = Column(Float, nullable=False, default=0)
    sugar_g = Column(Float, nullable=False, default=0)
    
    # Additional nutrients
    saturated_fat_g = Column(Float, nullable=True)
    trans_fat_g = Column(Float, nullable=True)
    cholesterol_mg = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    potassium_mg = Column(Float, nullable=True)
    
    # Vitamins (percentage of daily value)
    vitamin_a_percent = Column(Float, nullable=True)
    vitamin_c_percent = Column(Float, nullable=True)
    vitamin_d_percent = Column(Float, nullable=True)
    calcium_percent = Column(Float, nullable=True)
    iron_percent = Column(Float, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=True)  # "fruits", "vegetables", "protein", etc.
    image_url = Column(String(500), nullable=True)
    is_verified = Column(Integer, default=False)  # Admin verified entry
    source = Column(String(100), nullable=True)   # "usda", "user", "api"
    external_id = Column(String(100), nullable=True)  # ID from external database
    
    # Full nutrition data as JSON for less common nutrients
    extended_nutrition = Column(JSON, nullable=True)
    
    # Relationships
    nutrition_logs = relationship("NutritionLog", back_populates="food_entry")


class NutritionLog(BaseModel):
    """
    User's food consumption log
    Links users to food entries with quantity and meal context
    """
    __tablename__ = "nutrition_logs"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_entry_id = Column(Integer, ForeignKey("food_entries.id", ondelete="SET NULL"), nullable=True)
    
    # Log date and meal
    log_date = Column(Date, nullable=False, index=True)
    log_time = Column(DateTime, default=datetime.utcnow)
    meal_type = Column(SQLEnum(MealType), nullable=False)
    
    # Food details (denormalized for quick access and custom entries)
    food_name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True)
    
    # Quantity consumed
    quantity = Column(Float, nullable=False, default=1)
    serving_size = Column(Float, nullable=False)
    serving_unit = Column(String(50), nullable=False)
    
    # Calculated nutrition (based on quantity)
    calories = Column(Float, nullable=False, default=0)
    protein_g = Column(Float, nullable=False, default=0)
    carbohydrates_g = Column(Float, nullable=False, default=0)
    fat_g = Column(Float, nullable=False, default=0)
    fiber_g = Column(Float, nullable=False, default=0)
    sugar_g = Column(Float, nullable=False, default=0)
    sodium_mg = Column(Float, nullable=True)
    
    # Source tracking
    source = Column(SQLEnum(FoodSource), default=FoodSource.MANUAL)
    food_scan_id = Column(Integer, ForeignKey("food_scans.id"), nullable=True)
    
    # User notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="nutrition_logs")
    food_entry = relationship("FoodEntry", back_populates="nutrition_logs")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_nutrition_user_date', 'user_id', 'log_date'),
        Index('idx_nutrition_user_meal', 'user_id', 'log_date', 'meal_type'),
    )


class DailyNutritionSummary(BaseModel):
    """
    Pre-calculated daily nutrition totals
    Optimizes dashboard and reporting queries
    """
    __tablename__ = "daily_nutrition_summaries"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    summary_date = Column(Date, nullable=False)
    
    # Totals
    total_calories = Column(Float, default=0)
    total_protein_g = Column(Float, default=0)
    total_carbs_g = Column(Float, default=0)
    total_fat_g = Column(Float, default=0)
    total_fiber_g = Column(Float, default=0)
    total_sugar_g = Column(Float, default=0)
    total_sodium_mg = Column(Float, default=0)
    
    # Meal breakdown
    breakfast_calories = Column(Float, default=0)
    lunch_calories = Column(Float, default=0)
    dinner_calories = Column(Float, default=0)
    snacks_calories = Column(Float, default=0)
    
    # Goal progress (percentages)
    calorie_goal_percent = Column(Float, default=0)
    protein_goal_percent = Column(Float, default=0)
    carbs_goal_percent = Column(Float, default=0)
    fat_goal_percent = Column(Float, default=0)
    
    # Statistics
    meals_logged = Column(Integer, default=0)
    foods_logged = Column(Integer, default=0)
    
    # Unique constraint on user_id + date
    __table_args__ = (
        Index('idx_summary_user_date', 'user_id', 'summary_date', unique=True),
    )
