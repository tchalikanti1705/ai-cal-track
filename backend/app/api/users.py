"""
User Routes
User profile and goals management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.user_service import UserService
from app.schemas.user import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserGoalsCreate, UserGoalsUpdate, UserGoalsResponse,
    OnboardingSubmit, OnboardingProgress
)
from app.schemas.common import MessageResponse, DataResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


# ============ Profile Routes ============

@router.get("/profile", response_model=DataResponse[dict])
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile with calculated values
    """
    user_service = UserService(db)
    profile = user_service.get_profile_with_calculations(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return DataResponse(data=profile)


@router.post("/profile", response_model=DataResponse[UserProfileResponse])
async def create_profile(
    data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create user profile
    """
    user_service = UserService(db)
    
    # Check if profile exists
    existing = user_service.get_profile(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PATCH to update."
        )
    
    profile = user_service.create_profile(current_user.id, data)
    return DataResponse(data=profile)


@router.patch("/profile", response_model=DataResponse[UserProfileResponse])
async def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    user_service = UserService(db)
    profile = user_service.update_profile(current_user.id, data)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return DataResponse(data=profile)


# ============ Goals Routes ============

@router.get("/goals", response_model=DataResponse[UserGoalsResponse])
async def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's goals
    """
    user_service = UserService(db)
    goals = user_service.get_goals(current_user.id)
    
    if not goals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goals not found"
        )
    
    return DataResponse(data=goals)


@router.patch("/goals", response_model=DataResponse[UserGoalsResponse])
async def update_goals(
    data: UserGoalsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user goals
    """
    user_service = UserService(db)
    goals = user_service.update_goals(current_user.id, data)
    
    if not goals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goals not found"
        )
    
    return DataResponse(data=goals)


@router.get("/goals/recommended", response_model=DataResponse[dict])
async def get_recommended_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recommended nutrition goals based on profile
    """
    user_service = UserService(db)
    recommendations = user_service.calculate_recommended_goals(current_user.id)
    
    return DataResponse(data=recommendations)


# ============ Onboarding Routes ============

@router.get("/onboarding/questions", response_model=DataResponse[list])
async def get_onboarding_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get onboarding questions
    """
    user_service = UserService(db)
    questions = user_service.get_onboarding_questions()
    
    return DataResponse(data=questions)


@router.get("/onboarding/progress", response_model=DataResponse[OnboardingProgress])
async def get_onboarding_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get onboarding progress
    """
    user_service = UserService(db)
    progress = user_service.get_onboarding_progress(current_user.id)
    
    return DataResponse(data=progress)


@router.post("/onboarding/submit", response_model=MessageResponse)
async def submit_onboarding(
    data: OnboardingSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit onboarding responses
    """
    user_service = UserService(db)
    success, message = user_service.submit_onboarding_response(current_user.id, data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return MessageResponse(message=message)
