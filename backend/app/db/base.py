"""
SQLAlchemy Base Model with common functionality
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model with common columns and methods.
    All models should inherit from this class.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower() + 's'
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
