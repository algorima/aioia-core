"""
AIoIA Core - Core infrastructure for AIoIA projects.

Provides:
- Database: SQLAlchemy base models and CRUD repository
- Errors: Standardized error codes and responses
- Settings: Common settings classes
"""

from __future__ import annotations

import importlib
import warnings
from typing import Any

__version__ = "0.1.0"

from aioia_core.errors import (
    INTERNAL_SERVER_ERROR,
    RESOURCE_NOT_FOUND,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    ErrorResponse,
    extract_error_code_from_exception,
    get_error_detail_from_exception,
)
from aioia_core.factories.base_repository_factory import BaseRepositoryFactory
from aioia_core.models import Base, BaseModel
from aioia_core.repositories import BaseRepository
from aioia_core.types import (
    ConditionalFilter,
    ConditionalOperator,
    CrudFilter,
    CrudRepositoryProtocol,
    DatabaseRepositoryProtocol,
    FilterOperator,
    LogicalFilter,
    is_conditional_filter,
    is_logical_filter,
)
from aioia_core.settings import DatabaseSettings, JWTSettings, OpenAIAPISettings

__all__ = [
    # Database - New names (recommended)
    "Base",
    "BaseModel",
    "BaseRepository",
    "BaseRepositoryFactory",
    "CrudRepositoryProtocol",
    "DatabaseRepositoryProtocol",
    # Database - Deprecated aliases (backwards compatibility, via __getattr__)
    "BaseManager",  # pylint: disable=undefined-all-variable
    "BaseManagerFactory",  # pylint: disable=undefined-all-variable
    "CrudManagerProtocol",  # pylint: disable=undefined-all-variable
    "DatabaseManagerProtocol",  # pylint: disable=undefined-all-variable
    # Errors
    "ErrorResponse",
    "UNAUTHORIZED",
    "VALIDATION_ERROR",
    "RESOURCE_NOT_FOUND",
    "INTERNAL_SERVER_ERROR",
    "extract_error_code_from_exception",
    "get_error_detail_from_exception",
    # Filters
    "CrudFilter",
    "LogicalFilter",
    "ConditionalFilter",
    "FilterOperator",
    "ConditionalOperator",
    "is_logical_filter",
    "is_conditional_filter",
    # Settings
    "DatabaseSettings",
    "OpenAIAPISettings",
    "JWTSettings",
]

# Deprecated names for lazy loading via __getattr__
_DEPRECATED_NAMES = {
    "BaseManagerFactory": "aioia_core.factories.base_manager_factory",
    "BaseManager": "aioia_core.managers",
    "CrudManagerProtocol": "aioia_core.types",
    "DatabaseManagerProtocol": "aioia_core.types",
}


def __getattr__(name: str) -> Any:
    """PEP 562-style lazy loading of deprecated names."""
    if name in _DEPRECATED_NAMES:
        # Some imported modules issue their own DeprecationWarning.
        # For protocols, we issue a warning here as the module does not.
        if name in {"CrudManagerProtocol", "DatabaseManagerProtocol"}:
            new_name = name.replace("Manager", "Repository")
            warnings.warn(
                f"{name} is deprecated, use {new_name} instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        module = importlib.import_module(_DEPRECATED_NAMES[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """PEP 562-style module directory including deprecated names."""
    return list(__all__)
