"""
Water Tracking Pydantic Schemas
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.water import ContainerType


# ============ Water Log Schemas ============

class WaterLogCreate(BaseModel):
    """Create water log entry"""
    log_date: date
    amount_ml: int = Field(..., gt=0, le=5000)
    container_type: ContainerType = ContainerType.CUSTOM
    beverage_type: str = "water"


class WaterLogQuickAdd(BaseModel):
    """Quick add water with preset container"""
    container_type: ContainerType
    log_date: Optional[date] = None


class WaterLogResponse(BaseModel):
    """Water log response"""
    id: int
    user_id: int
    log_date: date
    log_time: datetime
    amount_ml: int
    container_type: ContainerType
    beverage_type: str
    
    class Config:
        from_attributes = True


# ============ Daily Water Summary ============

class DailyWaterSummary(BaseModel):
    """Daily water intake summary"""
    date: date
    total_ml: int = 0
    goal_ml: int = 2000
    goal_percent: float = 0
    remaining_ml: int = 0
    entries_count: int = 0
    entries: List[WaterLogResponse] = []
    
    # Breakdown by beverage type
    water_ml: int = 0
    other_ml: int = 0
    
    # Hourly breakdown for chart
    hourly_intake: dict = {}


class WeeklyWaterSummary(BaseModel):
    """Weekly water intake summary"""
    start_date: date
    end_date: date
    total_ml: int = 0
    daily_average_ml: float = 0
    goal_ml_daily: int = 2000
    days_on_goal: int = 0
    
    daily_breakdown: List[DailyWaterSummary] = []


# ============ Water Goal Schemas ============

class WaterGoalCreate(BaseModel):
    """Create water goal"""
    daily_goal_ml: int = Field(..., gt=0, le=10000)
    reminder_enabled: bool = True
    reminder_interval_minutes: int = Field(default=60, ge=15, le=240)
    reminder_start_time: str = "08:00"
    reminder_end_time: str = "22:00"


class WaterGoalUpdate(BaseModel):
    """Update water goal"""
    daily_goal_ml: Optional[int] = None
    reminder_enabled: Optional[bool] = None
    reminder_interval_minutes: Optional[int] = None
    reminder_start_time: Optional[str] = None
    reminder_end_time: Optional[str] = None


class WaterGoalResponse(BaseModel):
    """Water goal response"""
    id: int
    user_id: int
    daily_goal_ml: int
    reminder_enabled: bool
    reminder_interval_minutes: int
    reminder_start_time: str
    reminder_end_time: str
    effective_from: date
    
    class Config:
        from_attributes = True
