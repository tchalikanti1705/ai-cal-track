"""
User Models - User accounts, profiles, goals, and onboarding
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, Date, DateTime, 
    ForeignKey, Text, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ActivityLevel(enum.Enum):
    SEDENTARY = "sedentary"              # Little or no exercise
    LIGHTLY_ACTIVE = "lightly_active"     # Light exercise 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # Moderate exercise 3-5 days/week
    VERY_ACTIVE = "very_active"           # Hard exercise 6-7 days/week
    EXTRA_ACTIVE = "extra_active"         # Very hard exercise, physical job


class GoalType(enum.Enum):
    LOSE_WEIGHT = "lose_weight"
    GAIN_WEIGHT = "gain_weight"
    MAINTAIN_WEIGHT = "maintain_weight"
    BUILD_MUSCLE = "build_muscle"
    IMPROVE_HEALTH = "improve_health"


class DietaryPreference(enum.Enum):
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"


class User(BaseModel):
    """
    Core user model for authentication
    Follows single responsibility - only auth-related fields
    """
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Verification
    verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Login tracking
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    goals = relationship("UserGoals", back_populates="user", uselist=False, cascade="all, delete-orphan")
    onboarding_responses = relationship("OnboardingResponse", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = relationship("NutritionLog", back_populates="user", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="user", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", back_populates="user", cascade="all, delete-orphan")
    food_scans = relationship("FoodScan", back_populates="user", cascade="all, delete-orphan")
    walking_sessions = relationship("WalkingSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(BaseModel):
    """
    User profile with personal information and preferences
    Separated from User model for cleaner data management
    """
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal info
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    
    # Physical measurements
    height_cm = Column(Float, nullable=True)  # Height in centimeters
    current_weight_kg = Column(Float, nullable=True)  # Current weight in kg
    target_weight_kg = Column(Float, nullable=True)  # Target weight in kg
    
    # Activity and lifestyle
    activity_level = Column(SQLEnum(ActivityLevel), default=ActivityLevel.MODERATELY_ACTIVE)
    dietary_preference = Column(SQLEnum(DietaryPreference), default=DietaryPreference.NONE)
    
    # Allergies and restrictions (JSON array)
    allergies = Column(JSON, default=list)  # ["peanuts", "shellfish", etc.]
    health_conditions = Column(JSON, default=list)  # ["diabetes", "hypertension", etc.]
    
    # Profile settings
    timezone = Column(String(50), default="UTC")
    measurement_system = Column(String(10), default="metric")  # "metric" or "imperial"
    profile_image_url = Column(String(500), nullable=True)
    
    # Onboarding status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    @property
    def age(self) -> int:
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return 0
    
    @property
    def bmi(self) -> float:
        """Calculate BMI"""
        if self.height_cm and self.current_weight_kg:
            height_m = self.height_cm / 100
            return round(self.current_weight_kg / (height_m ** 2), 1)
        return 0.0
    
    def calculate_bmr(self) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
        """
        if not all([self.current_weight_kg, self.height_cm, self.date_of_birth, self.gender]):
            return 0.0
        
        age = self.age
        
        if self.gender == Gender.MALE:
            bmr = (10 * self.current_weight_kg) + (6.25 * self.height_cm) - (5 * age) + 5
        else:
            bmr = (10 * self.current_weight_kg) + (6.25 * self.height_cm) - (5 * age) - 161
        
        return round(bmr, 0)
    
    def calculate_tdee(self) -> float:
        """
        Calculate Total Daily Energy Expenditure
        BMR * Activity Multiplier
        """
        bmr = self.calculate_bmr()
        
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTRA_ACTIVE: 1.9
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.55)
        return round(bmr * multiplier, 0)


class UserGoals(BaseModel):
    """
    User nutrition and fitness goals
    Separate model for goal tracking and adjustments
    """
    __tablename__ = "user_goals"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Primary goal
    goal_type = Column(SQLEnum(GoalType), default=GoalType.MAINTAIN_WEIGHT)
    
    # Daily calorie goal (auto-calculated or custom)
    daily_calorie_goal = Column(Integer, nullable=True)
    is_calorie_goal_custom = Column(Boolean, default=False)
    
    # Macronutrient goals (in grams)
    protein_goal_g = Column(Integer, nullable=True)
    carbs_goal_g = Column(Integer, nullable=True)
    fat_goal_g = Column(Integer, nullable=True)
    fiber_goal_g = Column(Integer, default=25)
    
    # Other nutrition goals
    sodium_limit_mg = Column(Integer, default=2300)
    sugar_limit_g = Column(Integer, default=50)
    
    # Hydration goal
    water_goal_ml = Column(Integer, default=2000)  # 2 liters default
    
    # Exercise goals
    weekly_exercise_minutes = Column(Integer, default=150)  # WHO recommendation
    daily_steps_goal = Column(Integer, default=10000)
    weekly_workout_days = Column(Integer, default=3)
    
    # Weight goals
    weight_goal_kg = Column(Float, nullable=True)
    weight_change_rate = Column(Float, default=0.5)  # kg per week
    
    # Tracking preferences
    track_calories = Column(Boolean, default=True)
    track_macros = Column(Boolean, default=True)
    track_water = Column(Boolean, default=True)
    track_exercise = Column(Boolean, default=True)
    track_steps = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="goals")


class OnboardingResponse(BaseModel):
    """
    Stores user responses during onboarding flow
    Enables personalized goal setting and recommendations
    """
    __tablename__ = "onboarding_responses"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    question_key = Column(String(100), nullable=False)  # e.g., "primary_goal", "activity_level"
    question_text = Column(Text, nullable=False)
    response_value = Column(String(255), nullable=False)
    response_metadata = Column(JSON, nullable=True)  # Additional response data
    
    step_number = Column(Integer, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="onboarding_responses")
    
    class Config:
        # Unique constraint on user_id + question_key
        pass
