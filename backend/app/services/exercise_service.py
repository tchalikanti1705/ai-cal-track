"""
Exercise Service
Handles exercise logging and tracking
"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.exercise import Exercise, ExerciseLog, ExerciseType, ExerciseCategory, IntensityLevel
from app.models.user import UserProfile, UserGoals
from app.schemas.exercise import (
    ExerciseLogCreate, ExerciseLogUpdate,
    DailyExerciseSummary, WeeklyExerciseSummary
)

logger = get_logger(__name__)


class ExerciseService:
    """Exercise tracking service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ Exercise Library ============
    
    def get_exercise_types(self) -> List[ExerciseType]:
        """Get all exercise types"""
        return self.db.query(ExerciseType).order_by(ExerciseType.name).all()
    
    def get_exercise_type(self, type_id: int) -> Optional[ExerciseType]:
        """Get exercise type by ID"""
        return self.db.query(ExerciseType).filter(ExerciseType.id == type_id).first()
    
    def search_exercises(
        self,
        query: Optional[str] = None,
        category: Optional[ExerciseCategory] = None,
        limit: int = 20
    ) -> List[Exercise]:
        """Search exercise library"""
        q = self.db.query(Exercise)
        
        if query:
            q = q.filter(Exercise.name.ilike(f"%{query}%"))
        
        if category:
            q = q.filter(Exercise.category == category)
        
        return q.order_by(Exercise.popularity_score.desc()).limit(limit).all()
    
    # ============ Exercise Logging ============
    
    def log_exercise(self, user_id: int, data: ExerciseLogCreate) -> ExerciseLog:
        """Log exercise activity"""
        # Calculate calories if not provided
        calories_burned = data.calories_burned
        
        if not calories_burned or not data.is_calories_manual:
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            weight = profile.current_weight_kg if profile else 70  # Default weight
            
            calories_burned = self._calculate_calories_burned(
                duration_minutes=data.duration_minutes,
                intensity=data.intensity,
                weight_kg=weight,
                exercise_type_id=data.exercise_type_id
            )
        
        log = ExerciseLog(
            user_id=user_id,
            calories_burned=calories_burned,
            **data.model_dump(exclude={'calories_burned'})
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        logger.info(f"Exercise logged for user {user_id}: {data.exercise_name}")
        return log
    
    def get_exercise_log(self, log_id: int, user_id: int) -> Optional[ExerciseLog]:
        """Get specific exercise log"""
        return self.db.query(ExerciseLog).filter(
            ExerciseLog.id == log_id,
            ExerciseLog.user_id == user_id
        ).first()
    
    def update_exercise_log(
        self,
        log_id: int,
        user_id: int,
        data: ExerciseLogUpdate
    ) -> Optional[ExerciseLog]:
        """Update exercise log"""
        log = self.get_exercise_log(log_id, user_id)
        
        if not log:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(log, field, value)
        
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def delete_exercise_log(self, log_id: int, user_id: int) -> bool:
        """Delete exercise log"""
        log = self.get_exercise_log(log_id, user_id)
        
        if not log:
            return False
        
        self.db.delete(log)
        self.db.commit()
        
        logger.info(f"Exercise log deleted: {log_id}")
        return True
    
    def get_logs_by_date(self, user_id: int, log_date: date) -> List[ExerciseLog]:
        """Get all exercise logs for a date"""
        return self.db.query(ExerciseLog).filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.log_date == log_date
        ).order_by(ExerciseLog.start_time).all()
    
    def get_logs_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[ExerciseLog]:
        """Get exercise logs for date range"""
        return self.db.query(ExerciseLog).filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.log_date >= start_date,
            ExerciseLog.log_date <= end_date
        ).order_by(ExerciseLog.log_date, ExerciseLog.start_time).all()
    
    # ============ Summaries ============
    
    def get_daily_summary(self, user_id: int, summary_date: date) -> DailyExerciseSummary:
        """Get daily exercise summary"""
        logs = self.get_logs_by_date(user_id, summary_date)
        
        total_duration = sum(log.duration_minutes for log in logs)
        total_calories = sum(log.calories_burned for log in logs)
        
        cardio_minutes = sum(
            log.duration_minutes for log in logs 
            if log.category in [ExerciseCategory.CARDIO, ExerciseCategory.RUNNING, ExerciseCategory.CYCLING, ExerciseCategory.SWIMMING]
        )
        strength_minutes = sum(
            log.duration_minutes for log in logs 
            if log.category == ExerciseCategory.STRENGTH
        )
        flexibility_minutes = sum(
            log.duration_minutes for log in logs 
            if log.category in [ExerciseCategory.FLEXIBILITY, ExerciseCategory.YOGA]
        )
        
        return DailyExerciseSummary(
            date=summary_date,
            total_duration_minutes=total_duration,
            total_calories_burned=total_calories,
            exercises_count=len(logs),
            exercises=logs,
            cardio_minutes=cardio_minutes,
            strength_minutes=strength_minutes,
            flexibility_minutes=flexibility_minutes
        )
    
    def get_weekly_summary(self, user_id: int, start_date: date) -> WeeklyExerciseSummary:
        """Get weekly exercise summary"""
        end_date = start_date + timedelta(days=6)
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        weekly_goal = goals.weekly_exercise_minutes if goals else 150
        
        daily_breakdown = []
        total_duration = 0
        total_calories = 0
        total_exercises = 0
        workout_days = 0
        category_breakdown = {}
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            summary = self.get_daily_summary(user_id, current_date)
            daily_breakdown.append(summary)
            
            if summary.exercises_count > 0:
                workout_days += 1
                total_duration += summary.total_duration_minutes
                total_calories += summary.total_calories_burned
                total_exercises += summary.exercises_count
                
                for log in summary.exercises:
                    cat = log.category.value
                    category_breakdown[cat] = category_breakdown.get(cat, 0) + log.duration_minutes
        
        return WeeklyExerciseSummary(
            start_date=start_date,
            end_date=end_date,
            total_duration_minutes=total_duration,
            total_calories_burned=total_calories,
            total_exercises=total_exercises,
            workout_days=workout_days,
            weekly_goal_minutes=weekly_goal,
            goal_percent=(total_duration / weekly_goal * 100) if weekly_goal > 0 else 0,
            daily_breakdown=daily_breakdown,
            category_breakdown=category_breakdown
        )
    
    def _calculate_calories_burned(
        self,
        duration_minutes: int,
        intensity: IntensityLevel,
        weight_kg: float,
        exercise_type_id: Optional[int] = None
    ) -> float:
        """Calculate calories burned using MET formula"""
        # Default MET values by intensity
        met_values = {
            IntensityLevel.LIGHT: 3.0,
            IntensityLevel.MODERATE: 5.0,
            IntensityLevel.VIGOROUS: 8.0,
            IntensityLevel.MAXIMUM: 10.0
        }
        
        met = met_values.get(intensity, 5.0)
        
        # Override with exercise type MET if available
        if exercise_type_id:
            exercise_type = self.get_exercise_type(exercise_type_id)
            if exercise_type:
                met = getattr(exercise_type, f"met_{intensity.value}", met)
        
        # Calories = MET × Weight(kg) × Duration(hours)
        duration_hours = duration_minutes / 60
        calories = met * weight_kg * duration_hours
        
        return round(calories, 0)
