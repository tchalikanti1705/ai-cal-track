"""
Exercise Routes
Exercise logging and tracking
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.exercise_service import ExerciseService
from app.models.exercise import ExerciseCategory
from app.schemas.exercise import (
    ExerciseLogCreate, ExerciseLogUpdate, ExerciseLogResponse,
    ExerciseTypeResponse, ExerciseLibraryItem,
    DailyExerciseSummary, WeeklyExerciseSummary, QuickExerciseAdd
)
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


# ============ Exercise Library Routes ============

@router.get("/types", response_model=ListResponse[ExerciseTypeResponse])
async def get_exercise_types(
    db: Session = Depends(get_db)
):
    """
    Get all exercise types
    """
    exercise_service = ExerciseService(db)
    types = exercise_service.get_exercise_types()
    
    return ListResponse(data=types, total=len(types))


@router.get("/library", response_model=ListResponse[ExerciseLibraryItem])
async def search_exercises(
    query: Optional[str] = None,
    category: Optional[ExerciseCategory] = None,
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db)
):
    """
    Search exercise library
    """
    exercise_service = ExerciseService(db)
    exercises = exercise_service.search_exercises(query, category, limit)
    
    return ListResponse(data=exercises, total=len(exercises))


# ============ Exercise Log Routes ============

@router.post("/log", response_model=DataResponse[ExerciseLogResponse])
async def log_exercise(
    data: ExerciseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log exercise activity
    """
    exercise_service = ExerciseService(db)
    log = exercise_service.log_exercise(current_user.id, data)
    
    return DataResponse(data=log, message="Exercise logged")


@router.post("/log/quick", response_model=DataResponse[ExerciseLogResponse])
async def quick_log_exercise(
    data: QuickExerciseAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick add exercise with minimal details
    """
    exercise_service = ExerciseService(db)
    
    full_data = ExerciseLogCreate(
        log_date=data.log_date,
        exercise_name=data.exercise_name,
        category=data.category,
        duration_minutes=data.duration_minutes,
        intensity=data.intensity,
        calories_burned=data.calories_burned,
        is_calories_manual=data.calories_burned is not None
    )
    
    log = exercise_service.log_exercise(current_user.id, full_data)
    
    return DataResponse(data=log)


@router.get("/log/{log_id}", response_model=DataResponse[ExerciseLogResponse])
async def get_exercise_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific exercise log
    """
    exercise_service = ExerciseService(db)
    log = exercise_service.get_exercise_log(log_id, current_user.id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise log not found"
        )
    
    return DataResponse(data=log)


@router.patch("/log/{log_id}", response_model=DataResponse[ExerciseLogResponse])
async def update_exercise_log(
    log_id: int,
    data: ExerciseLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update exercise log
    """
    exercise_service = ExerciseService(db)
    log = exercise_service.update_exercise_log(log_id, current_user.id, data)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise log not found"
        )
    
    return DataResponse(data=log)


@router.delete("/log/{log_id}", response_model=MessageResponse)
async def delete_exercise_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete exercise log
    """
    exercise_service = ExerciseService(db)
    success = exercise_service.delete_exercise_log(log_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise log not found"
        )
    
    return MessageResponse(message="Exercise log deleted")


@router.get("/logs/date/{log_date}", response_model=ListResponse[ExerciseLogResponse])
async def get_logs_by_date(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all exercise logs for a date
    """
    exercise_service = ExerciseService(db)
    logs = exercise_service.get_logs_by_date(current_user.id, log_date)
    
    return ListResponse(data=logs, total=len(logs))


# ============ Summary Routes ============

@router.get("/summary/daily/{summary_date}", response_model=DataResponse[DailyExerciseSummary])
async def get_daily_summary(
    summary_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily exercise summary
    """
    exercise_service = ExerciseService(db)
    summary = exercise_service.get_daily_summary(current_user.id, summary_date)
    
    return DataResponse(data=summary)


@router.get("/summary/weekly/{start_date}", response_model=DataResponse[WeeklyExerciseSummary])
async def get_weekly_summary(
    start_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly exercise summary
    """
    exercise_service = ExerciseService(db)
    summary = exercise_service.get_weekly_summary(current_user.id, start_date)
    
    return DataResponse(data=summary)
