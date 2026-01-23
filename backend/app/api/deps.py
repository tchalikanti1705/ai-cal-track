"""
API Dependencies
Common dependencies for route handlers
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import verify_token
from app.core.logging_config import get_logger, set_correlation_id
from app.models.user import User

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token, token_type="access")
    
    if user_id is None:
        logger.warning("Invalid token provided")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        logger.warning(f"User not found for token: {user_id}")
        raise credentials_exception
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency that returns user if authenticated, None otherwise
    """
    if not token:
        return None
    
    try:
        user_id = verify_token(token, token_type="access")
        if user_id:
            return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        pass
    
    return None
