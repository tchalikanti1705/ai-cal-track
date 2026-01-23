"""
Walking/Steps Tracking Pydantic Schemas
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


# ============ Walking Session Schemas ============

class WalkingSessionCreate(BaseModel):
    """Create walking session"""
    session_date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(..., gt=0)
    steps: int = Field(..., ge=0)
    distance_meters: Optional[float] = None
    calories_burned: Optional[float] = None
    avg_pace_min_per_km: Optional[float] = None
    elevation_gain_m: Optional[float] = None
    activity_type: str = "walking"
    title: Optional[str] = None
    notes: Optional[str] = None
    is_outdoor: bool = True


class WalkingSessionUpdate(BaseModel):
    """Update walking session"""
    duration_minutes: Optional[int] = None
    steps: Optional[int] = None
    distance_meters: Optional[float] = None
    calories_burned: Optional[float] = None
    title: Optional[str] = None
    notes: Optional[str] = None


class WalkingSessionResponse(BaseModel):
    """Walking session response"""
    id: int
    user_id: int
    session_date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int
    steps: int
    distance_meters: Optional[float] = None
    calories_burned: Optional[float] = None
    avg_pace_min_per_km: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    elevation_gain_m: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    activity_type: str
    title: Optional[str] = None
    notes: Optional[str] = None
    is_outdoor: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Step Count Schemas ============

class StepCountCreate(BaseModel):
    """Create/Update daily step count"""
    count_date: date
    total_steps: int = Field(..., ge=0)
    step_goal: int = 10000
    total_distance_meters: Optional[float] = None
    total_calories_burned: Optional[float] = None
    active_minutes: int = 0


class StepCountResponse(BaseModel):
    """Daily step count response"""
    id: int
    user_id: int
    count_date: date
    total_steps: int
    step_goal: int
    goal_achieved: bool
    total_distance_meters: Optional[float] = None
    total_calories_burned: Optional[float] = None
    active_minutes: int
    walking_minutes: int
    running_minutes: int
    hourly_steps: Optional[dict] = None
    
    class Config:
        from_attributes = True


class QuickStepsAdd(BaseModel):
    """Quick add steps"""
    steps: int = Field(..., gt=0)
    date: Optional[date] = None


# ============ Walking Summary Schemas ============

class DailyWalkingSummary(BaseModel):
    """Daily walking summary"""
    date: date
    total_steps: int = 0
    step_goal: int = 10000
    goal_percent: float = 0
    goal_achieved: bool = False
    total_distance_km: float = 0
    total_calories_burned: float = 0
    active_minutes: int = 0
    sessions_count: int = 0
    sessions: List[WalkingSessionResponse] = []
    
    # Hourly breakdown
    hourly_steps: dict = {}


class WeeklyWalkingSummary(BaseModel):
    """Weekly walking summary"""
    start_date: date
    end_date: date
    total_steps: int = 0
    daily_average_steps: float = 0
    total_distance_km: float = 0
    total_calories_burned: float = 0
    total_active_minutes: int = 0
    days_goal_achieved: int = 0
    step_goal: int = 10000
    
    daily_breakdown: List[DailyWalkingSummary] = []
    
    # Trends
    best_day_steps: int = 0
    best_day_date: Optional[date] = None


class MonthlyWalkingSummary(BaseModel):
    """Monthly walking summary"""
    year: int
    month: int
    total_steps: int = 0
    daily_average_steps: float = 0
    total_distance_km: float = 0
    total_calories_burned: float = 0
    days_active: int = 0
    days_goal_achieved: int = 0
    
    weekly_breakdown: List[WeeklyWalkingSummary] = []
