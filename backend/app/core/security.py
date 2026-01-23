"""
Security Module
Handles password hashing, JWT token creation/validation, and authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


class TokenPayload:
    """JWT Token payload structure"""
    def __init__(self, sub: str, exp: datetime, token_type: str = "access"):
        self.sub = sub
        self.exp = exp
        self.token_type = token_type


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"Access token created for user: {subject}")
    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"Refresh token created for user: {subject}")
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token decode error: {e}")
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify token and return subject (user_id)"""
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != token_type:
        logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
        return None
    
    return payload.get("sub")


class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"
