"""
Walking/Steps Routes
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.walking_service import WalkingService
from app.schemas.walking import (
    WalkingSessionCreate, WalkingSessionUpdate, WalkingSessionResponse,
    StepCountCreate, StepCountResponse, QuickStepsAdd,
    DailyWalkingSummary, WeeklyWalkingSummary
)
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


# ============ Walking Session Routes ============

@router.post("/session", response_model=DataResponse[WalkingSessionResponse])
async def log_walking_session(
    data: WalkingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a walking session
    """
    walking_service = WalkingService(db)
    session = walking_service.log_walking_session(current_user.id, data)
    
    return DataResponse(data=session, message="Walking session logged")


@router.get("/session/{session_id}", response_model=DataResponse[WalkingSessionResponse])
async def get_walking_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific walking session
    """
    walking_service = WalkingService(db)
    session = walking_service.get_walking_session(session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walking session not found"
        )
    
    return DataResponse(data=session)


@router.patch("/session/{session_id}", response_model=DataResponse[WalkingSessionResponse])
async def update_walking_session(
    session_id: int,
    data: WalkingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update walking session
    """
    walking_service = WalkingService(db)
    session = walking_service.update_walking_session(session_id, current_user.id, data)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walking session not found"
        )
    
    return DataResponse(data=session)


@router.delete("/session/{session_id}", response_model=MessageResponse)
async def delete_walking_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete walking session
    """
    walking_service = WalkingService(db)
    success = walking_service.delete_walking_session(session_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Walking session not found"
        )
    
    return MessageResponse(message="Walking session deleted")


@router.get("/sessions/date/{session_date}", response_model=ListResponse[WalkingSessionResponse])
async def get_sessions_by_date(
    session_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get walking sessions for a date
    """
    walking_service = WalkingService(db)
    sessions = walking_service.get_sessions_by_date(current_user.id, session_date)
    
    return ListResponse(data=sessions, total=len(sessions))


# ============ Steps Routes ============

@router.post("/steps/add", response_model=DataResponse[StepCountResponse])
async def add_steps(
    data: QuickStepsAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick add steps
    """
    walking_service = WalkingService(db)
    step_count = walking_service.add_steps(current_user.id, data.steps, data.date)
    
    return DataResponse(data=step_count)


@router.get("/steps/{count_date}", response_model=DataResponse[StepCountResponse])
async def get_step_count(
    count_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get step count for a date
    """
    walking_service = WalkingService(db)
    step_count = walking_service.get_step_count(current_user.id, count_date)
    
    if not step_count:
        # Return empty response with goal
        from app.models.user import UserGoals
        goals = db.query(UserGoals).filter(UserGoals.user_id == current_user.id).first()
        
        return DataResponse(data={
            "count_date": count_date,
            "total_steps": 0,
            "step_goal": goals.daily_steps_goal if goals else 10000,
            "goal_achieved": False
        })
    
    return DataResponse(data=step_count)


@router.put("/steps", response_model=DataResponse[StepCountResponse])
async def update_step_count(
    data: StepCountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update or create daily step count
    """
    walking_service = WalkingService(db)
    step_count = walking_service.update_step_count(current_user.id, data)
    
    return DataResponse(data=step_count)


# ============ Summary Routes ============

@router.get("/summary/daily/{summary_date}", response_model=DataResponse[DailyWalkingSummary])
async def get_daily_summary(
    summary_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily walking summary
    """
    walking_service = WalkingService(db)
    summary = walking_service.get_daily_summary(current_user.id, summary_date)
    
    return DataResponse(data=summary)


@router.get("/summary/weekly/{start_date}", response_model=DataResponse[WeeklyWalkingSummary])
async def get_weekly_summary(
    start_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly walking summary
    """
    walking_service = WalkingService(db)
    summary = walking_service.get_weekly_summary(current_user.id, start_date)
    
    return DataResponse(data=summary)
