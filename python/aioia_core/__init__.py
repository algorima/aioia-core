"""
AIoIA Core - Core infrastructure for AIoIA projects.

Provides:
- Database: SQLAlchemy base models and CRUD manager
- Errors: Standardized error codes and responses
- Settings: Common settings classes
"""

__version__ = "0.1.0"

from aioia_core.database import Base, BaseManager, BaseModel
from aioia_core.errors import (
    INTERNAL_SERVER_ERROR,
    RESOURCE_NOT_FOUND,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    ErrorResponse,
    extract_error_code_from_exception,
    get_error_detail_from_exception,
)
from aioia_core.settings import JWTSettings, OpenAIAPISettings

__all__ = [
    # Database
    "Base",
    "BaseModel",
    "BaseManager",
    # Errors
    "ErrorResponse",
    "UNAUTHORIZED",
    "VALIDATION_ERROR",
    "RESOURCE_NOT_FOUND",
    "INTERNAL_SERVER_ERROR",
    "extract_error_code_from_exception",
    "get_error_detail_from_exception",
    # Settings
    "OpenAIAPISettings",
    "JWTSettings",
]
