"""
Deprecated: Use aioia_core.repositories instead.

This module provides backwards compatibility aliases for the renamed repository classes.
All classes have been renamed from *Manager to *Repository to follow industry standards.

Migration guide:
    # Old (deprecated)
    from aioia_core.managers import BaseManager

    # New (recommended)
    from aioia_core.repositories import BaseRepository
"""

from __future__ import annotations

import warnings

# Re-export from repositories module with deprecation warnings
from aioia_core.repositories import (
    BaseRepository,
    CreateSchemaType,
    DBModelType,
    ModelType,
    UpdateSchemaType,
)


def __getattr__(name: str):
    """Provide deprecated aliases for backwards compatibility."""
    if name == "BaseManager":
        warnings.warn(
            "BaseManager is deprecated, use BaseRepository instead. "
            "Import from aioia_core.repositories instead of aioia_core.managers",
            DeprecationWarning,
            stacklevel=2,
        )
        return BaseRepository

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Explicit alias for type checkers and static analysis
BaseManager = BaseRepository

__all__ = [
    # Deprecated alias (backwards compatibility)
    "BaseManager",
    # Re-exported types for compatibility
    "ModelType",
    "DBModelType",
    "CreateSchemaType",
    "UpdateSchemaType",
]
