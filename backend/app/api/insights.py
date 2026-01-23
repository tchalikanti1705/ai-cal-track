"""
Insights Routes
Analytics, trends, and recommendations
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.insights_service import InsightsService
from app.schemas.common import DataResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


@router.get("/dashboard", response_model=DataResponse[dict])
async def get_dashboard(
    target_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard data with all daily summaries
    """
    insights_service = InsightsService(db)
    dashboard = insights_service.get_dashboard_data(current_user.id, target_date)
    
    return DataResponse(data=dashboard)


@router.get("/trends/weekly", response_model=DataResponse[dict])
async def get_weekly_trends(
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly trend data for charts
    """
    insights_service = InsightsService(db)
    trends = insights_service.get_weekly_trends(current_user.id, end_date)
    
    return DataResponse(data=trends)


@router.get("/summary/monthly", response_model=DataResponse[dict])
async def get_monthly_summary(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly summary statistics
    """
    insights_service = InsightsService(db)
    summary = insights_service.get_monthly_summary(current_user.id, year, month)
    
    return DataResponse(data=summary)


@router.get("/macros", response_model=DataResponse[dict])
async def get_macro_distribution(
    target_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get macronutrient distribution for pie chart
    """
    insights_service = InsightsService(db)
    macros = insights_service.get_macro_distribution(current_user.id, target_date)
    
    return DataResponse(data=macros)


@router.get("/recommendations", response_model=DataResponse[list])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations
    """
    insights_service = InsightsService(db)
    recommendations = insights_service.get_recommendations(current_user.id)
    
    return DataResponse(data=recommendations)
