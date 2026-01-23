"""
Common Pydantic Schemas
Shared response models and base schemas
"""
from typing import TypeVar, Generic, Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    message: str = "Success"
    
    class Config:
        from_attributes = True


class DataResponse(BaseResponse, Generic[T]):
    """Response with data payload"""
    data: Optional[T] = None


class ListResponse(BaseResponse, Generic[T]):
    """Response with list data and pagination"""
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 1


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class DateRangeParams(BaseModel):
    """Date range filter parameters"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = "connected"
    cache: str = "connected"


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True
