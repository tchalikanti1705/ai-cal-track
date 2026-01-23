"""
Walking/Steps Tracking Models
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, 
    ForeignKey, Text, JSON, Index, Boolean
)
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class WalkingSession(BaseModel):
    """
    Individual walking/activity sessions
    Tracks walks with GPS data if available
    """
    __tablename__ = "walking_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session timing
    session_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=0)
    
    # Activity data
    steps = Column(Integer, nullable=False, default=0)
    distance_meters = Column(Float, nullable=True)
    calories_burned = Column(Float, nullable=True)
    
    # Pace and speed
    avg_pace_min_per_km = Column(Float, nullable=True)
    avg_speed_kmh = Column(Float, nullable=True)
    max_speed_kmh = Column(Float, nullable=True)
    
    # Elevation
    elevation_gain_m = Column(Float, nullable=True)
    elevation_loss_m = Column(Float, nullable=True)
    
    # Heart rate (if device connected)
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    
    # GPS route data (encoded polyline or array of coordinates)
    route_data = Column(JSON, nullable=True)
    
    # Activity type
    activity_type = Column(String(50), default="walking")  # walking, running, hiking
    
    # Session metadata
    title = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    weather = Column(String(100), nullable=True)
    is_outdoor = Column(Boolean, default=True)
    
    # Data source
    source = Column(String(50), default="manual")  # manual, phone, watch, fitness_tracker
    external_id = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="walking_sessions")
    
    __table_args__ = (
        Index('idx_walking_user_date', 'user_id', 'session_date'),
    )


class StepCount(BaseModel):
    """
    Daily step count summary
    Aggregated from sessions or synced from devices
    """
    __tablename__ = "step_counts"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    count_date = Column(Date, nullable=False)
    
    # Step counts
    total_steps = Column(Integer, nullable=False, default=0)
    step_goal = Column(Integer, nullable=False, default=10000)
    goal_achieved = Column(Boolean, default=False)
    
    # Distance and calories
    total_distance_meters = Column(Float, nullable=True)
    total_calories_burned = Column(Float, nullable=True)
    
    # Activity breakdown (in minutes)
    active_minutes = Column(Integer, default=0)
    walking_minutes = Column(Integer, default=0)
    running_minutes = Column(Integer, default=0)
    
    # Hourly breakdown (for charts)
    hourly_steps = Column(JSON, nullable=True)  # {0: 0, 1: 0, ..., 23: 500}
    
    # Data quality
    data_source = Column(String(50), default="calculated")
    last_sync = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_steps_user_date', 'user_id', 'count_date', unique=True),
    )
