"""
Application Configuration Module
Handles all environment variables and application settings using Pydantic
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Food Tracking"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/food_tracking"
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # JWT Authentication
    SECRET_KEY: str = Field(default="your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    FOOD_RECOGNITION_MODEL: str = "gpt-4-vision-preview"
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
