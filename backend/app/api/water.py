"""
Water Tracking Routes
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.water_service import WaterService
from app.models.water import ContainerType
from app.schemas.water import (
    WaterLogCreate, WaterLogQuickAdd, WaterLogResponse,
    WaterGoalCreate, WaterGoalUpdate, WaterGoalResponse,
    DailyWaterSummary, WeeklyWaterSummary
)
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


# ============ Water Log Routes ============

@router.post("/log", response_model=DataResponse[WaterLogResponse])
async def log_water(
    data: WaterLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log water intake
    """
    water_service = WaterService(db)
    log = water_service.log_water(current_user.id, data)
    
    return DataResponse(data=log, message="Water logged")


@router.post("/log/quick", response_model=DataResponse[WaterLogResponse])
async def quick_add_water(
    data: WaterLogQuickAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick add water with preset container
    """
    water_service = WaterService(db)
    log = water_service.quick_add_water(
        current_user.id,
        data.container_type,
        data.log_date
    )
    
    return DataResponse(data=log)


@router.get("/logs/date/{log_date}", response_model=ListResponse[WaterLogResponse])
async def get_logs_by_date(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all water logs for a date
    """
    water_service = WaterService(db)
    logs = water_service.get_logs_by_date(current_user.id, log_date)
    
    return ListResponse(data=logs, total=len(logs))


@router.delete("/log/{log_id}", response_model=MessageResponse)
async def delete_water_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete water log
    """
    water_service = WaterService(db)
    success = water_service.delete_water_log(log_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Water log not found"
        )
    
    return MessageResponse(message="Water log deleted")


# ============ Water Goal Routes ============

@router.get("/goal", response_model=DataResponse[WaterGoalResponse])
async def get_water_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current water goal
    """
    water_service = WaterService(db)
    goal = water_service.get_water_goal(current_user.id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Water goal not set"
        )
    
    return DataResponse(data=goal)


@router.post("/goal", response_model=DataResponse[WaterGoalResponse])
async def set_water_goal(
    data: WaterGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set water goal
    """
    water_service = WaterService(db)
    goal = water_service.set_water_goal(current_user.id, data)
    
    return DataResponse(data=goal, message="Water goal set")


@router.patch("/goal", response_model=DataResponse[WaterGoalResponse])
async def update_water_goal(
    data: WaterGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update water goal
    """
    water_service = WaterService(db)
    goal = water_service.update_water_goal(current_user.id, data)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Water goal not found"
        )
    
    return DataResponse(data=goal)


# ============ Summary Routes ============

@router.get("/summary/daily/{summary_date}", response_model=DataResponse[DailyWaterSummary])
async def get_daily_summary(
    summary_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily water intake summary
    """
    water_service = WaterService(db)
    summary = water_service.get_daily_summary(current_user.id, summary_date)
    
    return DataResponse(data=summary)


@router.get("/summary/weekly/{start_date}", response_model=DataResponse[WeeklyWaterSummary])
async def get_weekly_summary(
    start_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly water intake summary
    """
    water_service = WaterService(db)
    summary = water_service.get_weekly_summary(current_user.id, start_date)
    
    return DataResponse(data=summary)


# ============ Utility Routes ============

@router.get("/containers", response_model=DataResponse[dict])
async def get_container_sizes():
    """
    Get available container sizes
    """
    from app.models.water import CONTAINER_SIZES
    
    containers = [
        {"type": ct.value, "name": ct.name.replace("_", " ").title(), "ml": ml}
        for ct, ml in CONTAINER_SIZES.items()
    ]
    
    return DataResponse(data={"containers": containers})
