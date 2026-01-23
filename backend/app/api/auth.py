"""
Authentication Routes
Handles user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.logging_config import get_logger
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse,
    PasswordChange, TokenRefresh
)
from app.schemas.common import TokenResponse, MessageResponse, ErrorResponse
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    """
    auth_service = AuthService(db)
    user, error = auth_service.register_user(data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    tokens = auth_service.create_tokens(user.id)
    logger.info(f"New user registered: {user.email}")
    
    return tokens


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}}
)
async def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password (JSON body)
    Returns access and refresh tokens
    """
    auth_service = AuthService(db)
    
    user, error = auth_service.authenticate_user(data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    tokens = auth_service.create_tokens(user.id)
    
    return tokens


@router.post(
    "/login/json",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}}
)
async def login_json(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with JSON body (alternative to form)
    """
    auth_service = AuthService(db)
    user, error = auth_service.authenticate_user(data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return auth_service.create_tokens(user.id)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}}
)
async def refresh_token(
    data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    tokens = auth_service.refresh_access_token(data.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return tokens


@router.post(
    "/change-password",
    response_model=MessageResponse
)
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for current user
    """
    auth_service = AuthService(db)
    success, message = auth_service.change_password(
        current_user,
        data.current_password,
        data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return MessageResponse(message=message)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user
    Note: For JWT, logout is handled client-side by removing tokens
    For additional security, implement token blacklisting with Redis
    """
    logger.info(f"User logged out: {current_user.id}")
    return MessageResponse(message="Logged out successfully")
