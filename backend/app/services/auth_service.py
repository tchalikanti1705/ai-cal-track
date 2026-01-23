"""
Authentication Service
Handles user authentication, registration, and token management
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    validate_password_strength
)
from app.core.logging_config import get_logger
from app.core.config import settings
from app.models.user import User, UserProfile, UserGoals
from app.schemas.user import UserRegister, UserLogin
from app.schemas.common import TokenResponse

logger = get_logger(__name__)


class AuthService:
    """Authentication service with user management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, data: UserRegister) -> Tuple[User, str]:
        """
        Register a new user
        Returns (user, error_message)
        """
        logger.info(f"Attempting to register user: {data.email}")
        
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == data.email).first()
        if existing_user:
            logger.warning(f"Registration failed - email exists: {data.email}")
            return None, "Email already registered"
        
        # Validate password strength
        is_valid, message = validate_password_strength(data.password)
        if not is_valid:
            logger.warning(f"Registration failed - weak password: {data.email}")
            return None, message
        
        # Create user
        try:
            hashed_password = get_password_hash(data.password)
            
            user = User(
                email=data.email,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False
            )
            
            self.db.add(user)
            self.db.flush()  # Get user ID
            
            # Create empty profile
            profile = UserProfile(
                user_id=user.id,
                onboarding_completed=False,
                onboarding_step=0
            )
            self.db.add(profile)
            
            # Create default goals
            goals = UserGoals(
                user_id=user.id
            )
            self.db.add(goals)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User registered successfully: {user.id}")
            return user, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration error: {e}", exc_info=True)
            return None, "Registration failed. Please try again."
    
    def authenticate_user(self, data: UserLogin) -> Tuple[Optional[User], str]:
        """
        Authenticate user with email and password
        Returns (user, error_message)
        """
        logger.info(f"Login attempt: {data.email}")
        
        user = self.db.query(User).filter(User.email == data.email).first()
        
        if not user:
            logger.warning(f"Login failed - user not found: {data.email}")
            return None, "Invalid email or password"
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            logger.warning(f"Login failed - account locked: {data.email}")
            return None, "Account is temporarily locked. Please try again later."
        
        # Check if account is active
        if not user.is_active:
            logger.warning(f"Login failed - account inactive: {data.email}")
            return None, "Account is deactivated"
        
        # Verify password
        if not verify_password(data.password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                logger.warning(f"Account locked due to failed attempts: {data.email}")
            
            self.db.commit()
            logger.warning(f"Login failed - invalid password: {data.email}")
            return None, "Invalid email or password"
        
        # Successful login - reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"User logged in successfully: {user.id}")
        return user, None
    
    def create_tokens(self, user_id: int) -> TokenResponse:
        """Create access and refresh tokens for user"""
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_access_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """Refresh access token using refresh token"""
        user_id = verify_token(refresh_token, token_type="refresh")
        
        if not user_id:
            logger.warning("Token refresh failed - invalid refresh token")
            return None
        
        # Verify user still exists and is active
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            logger.warning(f"Token refresh failed - user invalid: {user_id}")
            return None
        
        logger.info(f"Token refreshed for user: {user_id}")
        return self.create_tokens(int(user_id))
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from access token"""
        user_id = verify_token(token, token_type="access")
        
        if not user_id:
            return None
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            return None
        
        return user
    
    def change_password(
        self, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> Tuple[bool, str]:
        """Change user password"""
        if not verify_password(current_password, user.hashed_password):
            return False, "Current password is incorrect"
        
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return False, message
        
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        logger.info(f"Password changed for user: {user.id}")
        return True, "Password changed successfully"
    
    def deactivate_user(self, user: User) -> bool:
        """Deactivate user account"""
        user.is_active = False
        self.db.commit()
        
        logger.info(f"User deactivated: {user.id}")
        return True
