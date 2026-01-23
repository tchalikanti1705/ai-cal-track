"""
Water Tracking Models - Hydration logs and goals
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, 
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class ContainerType(enum.Enum):
    GLASS = "glass"          # ~250ml
    CUP = "cup"              # ~200ml
    BOTTLE = "bottle"        # ~500ml
    LARGE_BOTTLE = "large_bottle"  # ~1000ml
    CUSTOM = "custom"


class WaterLog(BaseModel):
    """
    Individual water intake entries
    """
    __tablename__ = "water_logs"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timing
    log_date = Column(Date, nullable=False, index=True)
    log_time = Column(DateTime, default=datetime.utcnow)
    
    # Amount
    amount_ml = Column(Integer, nullable=False)
    container_type = Column(SQLEnum(ContainerType), default=ContainerType.CUSTOM)
    
    # Beverage type (mostly water, but can track other hydrating drinks)
    beverage_type = Column(String(50), default="water")  # water, tea, coffee, juice, etc.
    
    # Relationships
    user = relationship("User", back_populates="water_logs")
    
    __table_args__ = (
        Index('idx_water_user_date', 'user_id', 'log_date'),
    )


class WaterGoal(BaseModel):
    """
    User's daily water intake goal
    Separate from UserGoals for flexibility and history tracking
    """
    __tablename__ = "water_goals"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Goal settings
    daily_goal_ml = Column(Integer, nullable=False, default=2000)
    
    # Reminder settings
    reminder_enabled = Column(Integer, default=True)
    reminder_interval_minutes = Column(Integer, default=60)
    reminder_start_time = Column(String(5), default="08:00")  # HH:MM
    reminder_end_time = Column(String(5), default="22:00")
    
    # Effective dates (for goal history)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)  # NULL means current goal
    
    __table_args__ = (
        Index('idx_water_goal_user', 'user_id', 'effective_from'),
    )


# Container size presets (in ml)
CONTAINER_SIZES = {
    ContainerType.GLASS: 250,
    ContainerType.CUP: 200,
    ContainerType.BOTTLE: 500,
    ContainerType.LARGE_BOTTLE: 1000,
}
