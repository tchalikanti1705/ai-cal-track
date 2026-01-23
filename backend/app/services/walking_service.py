"""
Walking/Steps Tracking Service
"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.walking import WalkingSession, StepCount
from app.models.user import UserGoals
from app.schemas.walking import (
    WalkingSessionCreate, WalkingSessionUpdate, StepCountCreate,
    DailyWalkingSummary, WeeklyWalkingSummary
)

logger = get_logger(__name__)


class WalkingService:
    """Walking and steps tracking service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============ Walking Sessions ============
    
    def log_walking_session(
        self,
        user_id: int,
        data: WalkingSessionCreate
    ) -> WalkingSession:
        """Log a walking session"""
        # Calculate calories if not provided
        calories = data.calories_burned
        if not calories and data.steps:
            # Approximate: 0.04 calories per step
            calories = data.steps * 0.04
        
        session = WalkingSession(
            user_id=user_id,
            calories_burned=calories,
            **data.model_dump(exclude={'calories_burned'})
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Update daily step count
        self._update_daily_steps(user_id, data.session_date)
        
        logger.info(f"Walking session logged for user {user_id}: {data.steps} steps")
        return session
    
    def get_walking_session(
        self,
        session_id: int,
        user_id: int
    ) -> Optional[WalkingSession]:
        """Get specific walking session"""
        return self.db.query(WalkingSession).filter(
            WalkingSession.id == session_id,
            WalkingSession.user_id == user_id
        ).first()
    
    def update_walking_session(
        self,
        session_id: int,
        user_id: int,
        data: WalkingSessionUpdate
    ) -> Optional[WalkingSession]:
        """Update walking session"""
        session = self.get_walking_session(session_id, user_id)
        
        if not session:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        self.db.commit()
        self.db.refresh(session)
        
        self._update_daily_steps(user_id, session.session_date)
        
        return session
    
    def delete_walking_session(self, session_id: int, user_id: int) -> bool:
        """Delete walking session"""
        session = self.get_walking_session(session_id, user_id)
        
        if not session:
            return False
        
        session_date = session.session_date
        
        self.db.delete(session)
        self.db.commit()
        
        self._update_daily_steps(user_id, session_date)
        
        return True
    
    def get_sessions_by_date(
        self,
        user_id: int,
        session_date: date
    ) -> List[WalkingSession]:
        """Get walking sessions for a date"""
        return self.db.query(WalkingSession).filter(
            WalkingSession.user_id == user_id,
            WalkingSession.session_date == session_date
        ).order_by(WalkingSession.start_time).all()
    
    # ============ Step Counts ============
    
    def add_steps(self, user_id: int, steps: int, count_date: Optional[date] = None) -> StepCount:
        """Quick add steps to daily count"""
        target_date = count_date or date.today()
        
        step_count = self.db.query(StepCount).filter(
            StepCount.user_id == user_id,
            StepCount.count_date == target_date
        ).first()
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        step_goal = goals.daily_steps_goal if goals else 10000
        
        if step_count:
            step_count.total_steps += steps
            step_count.goal_achieved = step_count.total_steps >= step_goal
        else:
            step_count = StepCount(
                user_id=user_id,
                count_date=target_date,
                total_steps=steps,
                step_goal=step_goal,
                goal_achieved=steps >= step_goal
            )
            self.db.add(step_count)
        
        self.db.commit()
        self.db.refresh(step_count)
        
        return step_count
    
    def get_step_count(self, user_id: int, count_date: date) -> Optional[StepCount]:
        """Get step count for a date"""
        return self.db.query(StepCount).filter(
            StepCount.user_id == user_id,
            StepCount.count_date == count_date
        ).first()
    
    def update_step_count(
        self,
        user_id: int,
        data: StepCountCreate
    ) -> StepCount:
        """Update or create daily step count"""
        existing = self.get_step_count(user_id, data.count_date)
        
        if existing:
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing, field, value)
            existing.goal_achieved = existing.total_steps >= existing.step_goal
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        step_count = StepCount(
            user_id=user_id,
            goal_achieved=data.total_steps >= data.step_goal,
            **data.model_dump()
        )
        
        self.db.add(step_count)
        self.db.commit()
        self.db.refresh(step_count)
        
        return step_count
    
    # ============ Summaries ============
    
    def get_daily_summary(self, user_id: int, summary_date: date) -> DailyWalkingSummary:
        """Get daily walking summary"""
        sessions = self.get_sessions_by_date(user_id, summary_date)
        step_count = self.get_step_count(user_id, summary_date)
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        step_goal = goals.daily_steps_goal if goals else 10000
        
        if step_count:
            total_steps = step_count.total_steps
            total_distance = step_count.total_distance_meters or 0
            total_calories = step_count.total_calories_burned or 0
            active_minutes = step_count.active_minutes
            hourly_steps = step_count.hourly_steps or {}
        else:
            # Calculate from sessions
            total_steps = sum(s.steps for s in sessions)
            total_distance = sum(s.distance_meters or 0 for s in sessions)
            total_calories = sum(s.calories_burned or 0 for s in sessions)
            active_minutes = sum(s.duration_minutes for s in sessions)
            hourly_steps = {}
        
        return DailyWalkingSummary(
            date=summary_date,
            total_steps=total_steps,
            step_goal=step_goal,
            goal_percent=(total_steps / step_goal * 100) if step_goal > 0 else 0,
            goal_achieved=total_steps >= step_goal,
            total_distance_km=total_distance / 1000,
            total_calories_burned=total_calories,
            active_minutes=active_minutes,
            sessions_count=len(sessions),
            sessions=sessions,
            hourly_steps=hourly_steps
        )
    
    def get_weekly_summary(self, user_id: int, start_date: date) -> WeeklyWalkingSummary:
        """Get weekly walking summary"""
        end_date = start_date + timedelta(days=6)
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        step_goal = goals.daily_steps_goal if goals else 10000
        
        daily_breakdown = []
        total_steps = 0
        total_distance = 0
        total_calories = 0
        total_active_minutes = 0
        days_goal_achieved = 0
        best_day_steps = 0
        best_day_date = None
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            summary = self.get_daily_summary(user_id, current_date)
            daily_breakdown.append(summary)
            
            total_steps += summary.total_steps
            total_distance += summary.total_distance_km
            total_calories += summary.total_calories_burned
            total_active_minutes += summary.active_minutes
            
            if summary.goal_achieved:
                days_goal_achieved += 1
            
            if summary.total_steps > best_day_steps:
                best_day_steps = summary.total_steps
                best_day_date = current_date
        
        return WeeklyWalkingSummary(
            start_date=start_date,
            end_date=end_date,
            total_steps=total_steps,
            daily_average_steps=total_steps / 7,
            total_distance_km=total_distance,
            total_calories_burned=total_calories,
            total_active_minutes=total_active_minutes,
            days_goal_achieved=days_goal_achieved,
            step_goal=step_goal,
            daily_breakdown=daily_breakdown,
            best_day_steps=best_day_steps,
            best_day_date=best_day_date
        )
    
    def _update_daily_steps(self, user_id: int, count_date: date):
        """Update daily step count from walking sessions"""
        sessions = self.get_sessions_by_date(user_id, count_date)
        
        total_steps = sum(s.steps for s in sessions)
        total_distance = sum(s.distance_meters or 0 for s in sessions)
        total_calories = sum(s.calories_burned or 0 for s in sessions)
        total_duration = sum(s.duration_minutes for s in sessions)
        
        goals = self.db.query(UserGoals).filter(UserGoals.user_id == user_id).first()
        step_goal = goals.daily_steps_goal if goals else 10000
        
        step_count = self.get_step_count(user_id, count_date)
        
        if step_count:
            step_count.total_steps = total_steps
            step_count.total_distance_meters = total_distance
            step_count.total_calories_burned = total_calories
            step_count.walking_minutes = total_duration
            step_count.goal_achieved = total_steps >= step_goal
        else:
            step_count = StepCount(
                user_id=user_id,
                count_date=count_date,
                total_steps=total_steps,
                step_goal=step_goal,
                goal_achieved=total_steps >= step_goal,
                total_distance_meters=total_distance,
                total_calories_burned=total_calories,
                walking_minutes=total_duration
            )
            self.db.add(step_count)
        
        self.db.commit()
