"""
Comprehensive Logging Configuration
Provides structured logging with rotation, different handlers, and correlation IDs
"""
import logging
import logging.handlers
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextvars import ContextVar
import json

from .config import settings

# Context variable for request correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get or create correlation ID for request tracking"""
    cid = correlation_id_var.get()
    if cid is None:
        cid = str(uuid.uuid4())[:8]
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current context"""
    correlation_id_var.set(cid)


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> logging.Logger:
    """Configure application logging with multiple handlers"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Correlation ID filter
    correlation_filter = CorrelationIdFilter()
    
    # Console Handler (colored output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_format = "%(asctime)s | %(levelname)s | [%(correlation_id)s] | %(name)s:%(lineno)d | %(message)s"
    console_handler.setFormatter(ColoredFormatter(console_format))
    console_handler.addFilter(correlation_filter)
    root_logger.addHandler(console_handler)
    
    # File Handler - General logs (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(correlation_filter)
    root_logger.addHandler(file_handler)
    
    # Error File Handler - Only errors
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    error_handler.addFilter(correlation_filter)
    root_logger.addHandler(error_handler)
    
    # Access log handler - for HTTP requests
    access_logger = logging.getLogger("access")
    access_handler = logging.handlers.RotatingFileHandler(
        log_dir / "access.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    access_handler.setFormatter(JSONFormatter())
    access_handler.addFilter(correlation_filter)
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


class AppLogger:
    """Application logger with extra context support"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log(self, level: int, message: str, extra_data: dict = None, **kwargs):
        if extra_data:
            kwargs["extra"] = {"extra_data": extra_data}
        self.logger.log(level, message, **kwargs)
    
    def debug(self, message: str, extra_data: dict = None):
        self._log(logging.DEBUG, message, extra_data)
    
    def info(self, message: str, extra_data: dict = None):
        self._log(logging.INFO, message, extra_data)
    
    def warning(self, message: str, extra_data: dict = None):
        self._log(logging.WARNING, message, extra_data)
    
    def error(self, message: str, extra_data: dict = None, exc_info: bool = False):
        self._log(logging.ERROR, message, extra_data, exc_info=exc_info)
    
    def critical(self, message: str, extra_data: dict = None, exc_info: bool = False):
        self._log(logging.CRITICAL, message, extra_data, exc_info=exc_info)


def get_logger(name: str) -> AppLogger:
    """Factory function to get a logger instance"""
    return AppLogger(name)
