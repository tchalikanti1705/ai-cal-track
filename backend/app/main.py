"""
AI Food Tracking - Main Application
FastAPI application with comprehensive middleware and error handling
"""
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger, set_correlation_id
from app.db.database import init_db, check_db_connection
from app.api import api_router

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    logger.info("Starting AI Food Tracking API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Check database connection
    if not check_db_connection():
        logger.warning("Database connection check failed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Food Tracking API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI-Powered Food Tracking API
    
    A comprehensive health and nutrition tracking platform with:
    - 🔐 User authentication and profiles
    - 🍎 AI-powered food scanning
    - 📊 Calorie and macro tracking
    - 💧 Water intake tracking
    - 🏃 Exercise logging
    - 👣 Walking/steps tracking
    - 📈 Insights and analytics
    """,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and logging middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Add request ID and log requests"""
    # Generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
    set_correlation_id(correlation_id)
    
    # Log request start
    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        raise
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Add headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    # Log request completion
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = exc.errors()
    logger.warning(f"Validation error: {errors}")
    
    # Format error messages
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": error_messages
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
