"""
Food Scan Models - AI-powered food recognition
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, Text, Enum as SQLEnum, JSON, Index, Boolean
)
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class ScanStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class ScanType(enum.Enum):
    PHOTO = "photo"
    BARCODE = "barcode"
    RECEIPT = "receipt"
    MENU = "menu"


class FoodScan(BaseModel):
    """
    Food scan request and results
    Stores the image/barcode and AI analysis results
    """
    __tablename__ = "food_scans"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scan type and status
    scan_type = Column(SQLEnum(ScanType), default=ScanType.PHOTO)
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.PENDING)
    
    # Image/barcode data
    image_url = Column(String(500), nullable=True)
    image_base64 = Column(Text, nullable=True)  # For immediate processing
    barcode = Column(String(50), nullable=True)
    
    # Timing
    scanned_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # AI Model info
    model_used = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)  # Overall confidence 0-1
    
    # Raw AI response
    raw_response = Column(JSON, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # User feedback
    user_confirmed = Column(Boolean, nullable=True)
    user_corrected = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="food_scans")
    results = relationship("FoodScanResult", back_populates="scan", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_scan_user_date', 'user_id', 'scanned_at'),
        Index('idx_scan_status', 'status'),
    )


class FoodScanResult(BaseModel):
    """
    Individual food items detected in a scan
    A single scan can identify multiple food items
    """
    __tablename__ = "food_scan_results"
    
    scan_id = Column(Integer, ForeignKey("food_scans.id", ondelete="CASCADE"), nullable=False)
    
    # Detected food
    food_name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)  # 0-1
    
    # Position in image (for multi-food detection)
    bounding_box = Column(JSON, nullable=True)  # {x, y, width, height}
    
    # Estimated portion
    estimated_portion = Column(String(100), nullable=True)
    estimated_weight_g = Column(Float, nullable=True)
    
    # Nutrition (estimated by AI)
    estimated_calories = Column(Float, nullable=True)
    estimated_protein_g = Column(Float, nullable=True)
    estimated_carbs_g = Column(Float, nullable=True)
    estimated_fat_g = Column(Float, nullable=True)
    
    # Full nutrition data
    nutrition_data = Column(JSON, nullable=True)
    
    # Matched to existing food entry
    matched_food_entry_id = Column(Integer, ForeignKey("food_entries.id"), nullable=True)
    match_confidence = Column(Float, nullable=True)
    
    # Alternative matches
    alternative_matches = Column(JSON, nullable=True)  # [{name, confidence, nutrition}, ...]
    
    # User corrections
    user_selected_name = Column(String(255), nullable=True)
    user_adjusted_portion = Column(Float, nullable=True)
    
    # Added to log
    added_to_log = Column(Boolean, default=False)
    nutrition_log_id = Column(Integer, nullable=True)
    
    # Relationships
    scan = relationship("FoodScan", back_populates="results")
    
    __table_args__ = (
        Index('idx_result_scan', 'scan_id'),
    )
