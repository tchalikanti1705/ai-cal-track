"""
Exercise Models - Exercise types, logs, and tracking
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, 
    ForeignKey, Text, Enum as SQLEnum, JSON, Index, Boolean
)
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class ExerciseCategory(enum.Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    SPORTS = "sports"
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    YOGA = "yoga"
    HIIT = "hiit"
    OTHER = "other"


class IntensityLevel(enum.Enum):
    LIGHT = "light"
    MODERATE = "moderate"
    VIGOROUS = "vigorous"
    MAXIMUM = "maximum"


class ExerciseType(BaseModel):
    """
    Exercise type definitions with MET values for calorie calculation
    MET = Metabolic Equivalent of Task
    """
    __tablename__ = "exercise_types"
    
    name = Column(String(255), nullable=False, unique=True)
    category = Column(SQLEnum(ExerciseCategory), nullable=False)
    description = Column(Text, nullable=True)
    
    # MET values for different intensities
    met_light = Column(Float, default=3.0)
    met_moderate = Column(Float, default=5.0)
    met_vigorous = Column(Float, default=8.0)
    met_maximum = Column(Float, default=10.0)
    
    # Default intensity
    default_intensity = Column(SQLEnum(IntensityLevel), default=IntensityLevel.MODERATE)
    
    # Exercise attributes
    is_cardio = Column(Boolean, default=False)
    is_strength = Column(Boolean, default=False)
    burns_calories = Column(Boolean, default=True)
    
    # Icon/image
    icon = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Relationships
    exercise_logs = relationship("ExerciseLog", back_populates="exercise_type")


class ExerciseLog(BaseModel):
    """
    User exercise activity log
    """
    __tablename__ = "exercise_logs"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_type_id = Column(Integer, ForeignKey("exercise_types.id"), nullable=True)
    
    # Timing
    log_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    
    # Exercise details
    exercise_name = Column(String(255), nullable=False)
    category = Column(SQLEnum(ExerciseCategory), nullable=False)
    intensity = Column(SQLEnum(IntensityLevel), default=IntensityLevel.MODERATE)
    
    # Calories burned (calculated or manual)
    calories_burned = Column(Float, nullable=False, default=0)
    is_calories_manual = Column(Boolean, default=False)
    
    # For cardio exercises
    distance_km = Column(Float, nullable=True)
    pace_min_per_km = Column(Float, nullable=True)
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    
    # For strength exercises
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    weather = Column(String(100), nullable=True)
    
    # Tracking source
    source = Column(String(50), default="manual")  # "manual", "device", "app"
    external_id = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="exercise_logs")
    exercise_type = relationship("ExerciseType", back_populates="exercise_logs")
    
    __table_args__ = (
        Index('idx_exercise_user_date', 'user_id', 'log_date'),
    )
    
    def calculate_calories_burned(self, weight_kg: float) -> float:
        """
        Calculate calories burned using MET formula
        Calories = MET × Weight(kg) × Duration(hours)
        """
        met_values = {
            IntensityLevel.LIGHT: 3.0,
            IntensityLevel.MODERATE: 5.0,
            IntensityLevel.VIGOROUS: 8.0,
            IntensityLevel.MAXIMUM: 10.0
        }
        
        if self.exercise_type:
            met = getattr(self.exercise_type, f"met_{self.intensity.value}", 5.0)
        else:
            met = met_values.get(self.intensity, 5.0)
        
        duration_hours = self.duration_minutes / 60
        calories = met * weight_kg * duration_hours
        
        return round(calories, 0)


class Exercise(BaseModel):
    """
    Predefined exercise library for quick selection
    """
    __tablename__ = "exercises"
    
    name = Column(String(255), nullable=False)
    category = Column(SQLEnum(ExerciseCategory), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # MET value
    met_value = Column(Float, default=5.0)
    
    # Typical duration
    typical_duration_minutes = Column(Integer, default=30)
    
    # Muscle groups targeted (for strength exercises)
    muscle_groups = Column(JSON, default=list)  # ["chest", "triceps", etc.]
    
    # Equipment needed
    equipment = Column(JSON, default=list)  # ["dumbbells", "barbell", etc.]
    
    # Difficulty
    difficulty_level = Column(String(20), default="intermediate")
    
    # Media
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    
    # Popularity for sorting
    popularity_score = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_exercise_category', 'category'),
        Index('idx_exercise_name', 'name'),
    )
