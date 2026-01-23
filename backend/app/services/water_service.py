"""
Water Tracking Service
Handles water intake logging and tracking
"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.water import WaterLog, WaterGoal, ContainerType, CONTAINER_SIZES
from app.models.user import UserGoals
from app.schemas.water import (
    WaterLogCreate, WaterGoalCreate, WaterGoalUpdate,
    DailyWaterSummary, WeeklyWaterSummary
)

logger = get_logger(__name__)


class WaterService:
    """Water tracking service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ Water Logging ============
    
    def log_water(self, user_id: int, data: WaterLogCreate) -> WaterLog:
        """Log water intake"""
        log = WaterLog(
            user_id=user_id,
            **data.model_dump()
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        logger.info(f"Water logged for user {user_id}: {data.amount_ml}ml")
        return log
    
    def quick_add_water(
        self,
        user_id: int,
        container_type: ContainerType,
        log_date: Optional[date] = None
    ) -> WaterLog:
        """Quick add water with preset container size"""
        amount = CONTAINER_SIZES.get(container_type, 250)
        
        log = WaterLog(
            user_id=user_id,
            log_date=log_date or date.today(),
            amount_ml=amount,
            container_type=container_type,
            beverage_type="water"
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def get_water_log(self, log_id: int, user_id: int) -> Optional[WaterLog]:
        """Get specific water log"""
        return self.db.query(WaterLog).filter(
            WaterLog.id == log_id,
            WaterLog.user_id == user_id
        ).first()
    
    def delete_water_log(self, log_id: int, user_id: int) -> bool:
        """Delete water log"""
        log = self.get_water_log(log_id, user_id)
        
        if not log:
            return False
        
        self.db.delete(log)
        self.db.commit()
        
        return True
    
    def get_logs_by_date(self, user_id: int, log_date: date) -> List[WaterLog]:
        """Get all water logs for a date"""
        return self.db.query(WaterLog).filter(
            WaterLog.user_id == user_id,
            WaterLog.log_date == log_date
        ).order_by(WaterLog.log_time).all()
    
    # ============ Water Goals ============
    
    def get_water_goal(self, user_id: int) -> Optional[WaterGoal]:
        """Get current water goal"""
        return self.db.query(WaterGoal).filter(
            WaterGoal.user_id == user_id,
            WaterGoal.effective_to == None
        ).first()
    
    def set_water_goal(self, user_id: int, data: WaterGoalCreate) -> WaterGoal:
        """Set or update water goal"""
        # Expire current goal
        current_goal = self.get_water_goal(user_id)
        if current_goal:
            current_goal.effective_to = date.today() - timedelta(days=1)
        
        # Create new goal
        goal = WaterGoal(
            user_id=user_id,
            effective_from=date.today(),
            **data.model_dump()
        )
        
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        
        # Also update UserGoals
        user_goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        if user_goals:
            user_goals.water_goal_ml = data.daily_goal_ml
            self.db.commit()
        
        return goal
    
    def update_water_goal(
        self,
        user_id: int,
        data: WaterGoalUpdate
    ) -> Optional[WaterGoal]:
        """Update current water goal"""
        goal = self.get_water_goal(user_id)
        
        if not goal:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        self.db.commit()
        self.db.refresh(goal)
        
        return goal
    
    # ============ Summaries ============
    
    def get_daily_summary(self, user_id: int, summary_date: date) -> DailyWaterSummary:
        """Get daily water intake summary"""
        logs = self.get_logs_by_date(user_id, summary_date)
        
        # Get goal
        goal = self.get_water_goal(user_id)
        user_goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        
        goal_ml = 2000  # Default
        if goal:
            goal_ml = goal.daily_goal_ml
        elif user_goals:
            goal_ml = user_goals.water_goal_ml
        
        total_ml = sum(log.amount_ml for log in logs)
        water_ml = sum(log.amount_ml for log in logs if log.beverage_type == "water")
        other_ml = total_ml - water_ml
        
        # Build hourly breakdown
        hourly_intake = {}
        for log in logs:
            hour = log.log_time.hour
            hourly_intake[hour] = hourly_intake.get(hour, 0) + log.amount_ml
        
        return DailyWaterSummary(
            date=summary_date,
            total_ml=total_ml,
            goal_ml=goal_ml,
            goal_percent=(total_ml / goal_ml * 100) if goal_ml > 0 else 0,
            remaining_ml=max(0, goal_ml - total_ml),
            entries_count=len(logs),
            entries=logs,
            water_ml=water_ml,
            other_ml=other_ml,
            hourly_intake=hourly_intake
        )
    
    def get_weekly_summary(self, user_id: int, start_date: date) -> WeeklyWaterSummary:
        """Get weekly water intake summary"""
        end_date = start_date + timedelta(days=6)
        
        daily_breakdown = []
        total_ml = 0
        days_on_goal = 0
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            summary = self.get_daily_summary(user_id, current_date)
            daily_breakdown.append(summary)
            
            total_ml += summary.total_ml
            if summary.total_ml >= summary.goal_ml:
                days_on_goal += 1
        
        goal = self.get_water_goal(user_id)
        goal_ml_daily = goal.daily_goal_ml if goal else 2000
        
        return WeeklyWaterSummary(
            start_date=start_date,
            end_date=end_date,
            total_ml=total_ml,
            daily_average_ml=total_ml / 7,
            goal_ml_daily=goal_ml_daily,
            days_on_goal=days_on_goal,
            daily_breakdown=daily_breakdown
        )
