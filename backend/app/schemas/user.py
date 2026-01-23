"""
User Pydantic Schemas
Request/Response models for user-related endpoints
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import Gender, ActivityLevel, GoalType, DietaryPreference


# ============ Authentication Schemas ============

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordChange(BaseModel):
    """Password change request (logged in user)"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


# ============ User Response Schemas ============

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response (public data)"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None


class UserWithProfile(UserResponse):
    """User with profile data"""
    profile: Optional['UserProfileResponse'] = None
    goals: Optional['UserGoalsResponse'] = None


# ============ Profile Schemas ============

class UserProfileCreate(BaseModel):
    """Create user profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    height_cm: Optional[float] = Field(None, gt=0, lt=300)
    current_weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    target_weight_kg: Optional[float] = Field(None, gt=0, lt=500)
    activity_level: Optional[ActivityLevel] = ActivityLevel.MODERATELY_ACTIVE
    dietary_preference: Optional[DietaryPreference] = DietaryPreference.NONE
    allergies: List[str] = []
    health_conditions: List[str] = []
    timezone: str = "UTC"
    measurement_system: str = "metric"


class UserProfileUpdate(BaseModel):
    """Update user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    height_cm: Optional[float] = None
    current_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    dietary_preference: Optional[DietaryPreference] = None
    allergies: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    timezone: Optional[str] = None
    measurement_system: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    height_cm: Optional[float] = None
    current_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    dietary_preference: Optional[DietaryPreference] = None
    allergies: List[str] = []
    health_conditions: List[str] = []
    timezone: str = "UTC"
    measurement_system: str = "metric"
    profile_image_url: Optional[str] = None
    onboarding_completed: bool = False
    onboarding_step: int = 0
    
    # Calculated fields
    age: Optional[int] = None
    bmi: Optional[float] = None
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    
    class Config:
        from_attributes = True


# ============ Goals Schemas ============

class UserGoalsCreate(BaseModel):
    """Create user goals"""
    goal_type: GoalType = GoalType.MAINTAIN_WEIGHT
    daily_calorie_goal: Optional[int] = None
    protein_goal_g: Optional[int] = None
    carbs_goal_g: Optional[int] = None
    fat_goal_g: Optional[int] = None
    fiber_goal_g: int = 25
    water_goal_ml: int = 2000
    weekly_exercise_minutes: int = 150
    daily_steps_goal: int = 10000
    weight_goal_kg: Optional[float] = None


class UserGoalsUpdate(BaseModel):
    """Update user goals"""
    goal_type: Optional[GoalType] = None
    daily_calorie_goal: Optional[int] = None
    is_calorie_goal_custom: Optional[bool] = None
    protein_goal_g: Optional[int] = None
    carbs_goal_g: Optional[int] = None
    fat_goal_g: Optional[int] = None
    fiber_goal_g: Optional[int] = None
    sodium_limit_mg: Optional[int] = None
    sugar_limit_g: Optional[int] = None
    water_goal_ml: Optional[int] = None
    weekly_exercise_minutes: Optional[int] = None
    daily_steps_goal: Optional[int] = None
    weekly_workout_days: Optional[int] = None
    weight_goal_kg: Optional[float] = None
    weight_change_rate: Optional[float] = None
    track_calories: Optional[bool] = None
    track_macros: Optional[bool] = None
    track_water: Optional[bool] = None
    track_exercise: Optional[bool] = None
    track_steps: Optional[bool] = None


class UserGoalsResponse(BaseModel):
    """User goals response"""
    id: int
    user_id: int
    goal_type: GoalType
    daily_calorie_goal: Optional[int] = None
    is_calorie_goal_custom: bool = False
    protein_goal_g: Optional[int] = None
    carbs_goal_g: Optional[int] = None
    fat_goal_g: Optional[int] = None
    fiber_goal_g: int = 25
    sodium_limit_mg: int = 2300
    sugar_limit_g: int = 50
    water_goal_ml: int = 2000
    weekly_exercise_minutes: int = 150
    daily_steps_goal: int = 10000
    weekly_workout_days: int = 3
    weight_goal_kg: Optional[float] = None
    weight_change_rate: float = 0.5
    track_calories: bool = True
    track_macros: bool = True
    track_water: bool = True
    track_exercise: bool = True
    track_steps: bool = True
    
    class Config:
        from_attributes = True


# ============ Onboarding Schemas ============

class OnboardingQuestion(BaseModel):
    """Single onboarding question"""
    key: str
    text: str
    type: str  # "single_choice", "multiple_choice", "text", "number", "date"
    options: Optional[List[dict]] = None
    required: bool = True


class OnboardingResponse(BaseModel):
    """User's response to onboarding question"""
    question_key: str
    response_value: str
    response_metadata: Optional[dict] = None


class OnboardingSubmit(BaseModel):
    """Submit multiple onboarding responses"""
    responses: List[OnboardingResponse]
    step_number: int


class OnboardingProgress(BaseModel):
    """Onboarding progress status"""
    current_step: int
    total_steps: int
    completed: bool
    responses: List[dict] = []


# Forward references
UserWithProfile.model_rebuild()
