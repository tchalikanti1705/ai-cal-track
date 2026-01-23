"""
Exercise Pydantic Schemas
Request/Response models for exercise tracking
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.exercise import ExerciseCategory, IntensityLevel


# ============ Exercise Type Schemas ============

class ExerciseTypeResponse(BaseModel):
    """Exercise type response"""
    id: int
    name: str
    category: ExerciseCategory
    description: Optional[str] = None
    met_light: float
    met_moderate: float
    met_vigorous: float
    default_intensity: IntensityLevel
    is_cardio: bool
    is_strength: bool
    icon: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============ Exercise Log Schemas ============

class ExerciseLogCreate(BaseModel):
    """Create exercise log"""
    exercise_type_id: Optional[int] = None
    log_date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(..., gt=0)
    exercise_name: str = Field(..., max_length=255)
    category: ExerciseCategory
    intensity: IntensityLevel = IntensityLevel.MODERATE
    calories_burned: Optional[float] = None
    is_calories_manual: bool = False
    distance_km: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None
    location: Optional[str] = None


class ExerciseLogUpdate(BaseModel):
    """Update exercise log"""
    duration_minutes: Optional[int] = None
    intensity: Optional[IntensityLevel] = None
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None


class ExerciseLogResponse(BaseModel):
    """Exercise log response"""
    id: int
    user_id: int
    exercise_type_id: Optional[int] = None
    log_date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int
    exercise_name: str
    category: ExerciseCategory
    intensity: IntensityLevel
    calories_burned: float
    is_calories_manual: bool
    distance_km: Optional[float] = None
    pace_min_per_km: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuickExerciseAdd(BaseModel):
    """Quick add exercise with minimal details"""
    log_date: date
    exercise_name: str
    category: ExerciseCategory = ExerciseCategory.OTHER
    duration_minutes: int = Field(..., gt=0)
    intensity: IntensityLevel = IntensityLevel.MODERATE
    calories_burned: Optional[float] = None


# ============ Daily Exercise Summary ============

class DailyExerciseSummary(BaseModel):
    """Daily exercise summary"""
    date: date
    total_duration_minutes: int = 0
    total_calories_burned: float = 0
    exercises_count: int = 0
    exercises: List[ExerciseLogResponse] = []
    
    # By category
    cardio_minutes: int = 0
    strength_minutes: int = 0
    flexibility_minutes: int = 0


class WeeklyExerciseSummary(BaseModel):
    """Weekly exercise summary"""
    start_date: date
    end_date: date
    total_duration_minutes: int = 0
    total_calories_burned: float = 0
    total_exercises: int = 0
    workout_days: int = 0
    
    # Goals
    weekly_goal_minutes: int = 150
    goal_percent: float = 0
    
    daily_breakdown: List[DailyExerciseSummary] = []
    
    # By category
    category_breakdown: dict = {}


# ============ Exercise Library ============

class ExerciseLibraryItem(BaseModel):
    """Exercise from library"""
    id: int
    name: str
    category: ExerciseCategory
    description: Optional[str] = None
    instructions: Optional[str] = None
    met_value: float
    typical_duration_minutes: int
    muscle_groups: List[str] = []
    equipment: List[str] = []
    difficulty_level: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExerciseSearch(BaseModel):
    """Search exercises"""
    query: Optional[str] = None
    category: Optional[ExerciseCategory] = None
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    limit: int = Field(default=20, le=50)
