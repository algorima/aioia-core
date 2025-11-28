"""
Deprecated: Use aioia_core.factories.base_repository_factory instead.

This module provides backwards compatibility aliases for the renamed factory classes.
All classes have been renamed from *ManagerFactory to *RepositoryFactory to follow
industry standards.

Migration guide:
    # Old (deprecated)
    from aioia_core.factories.base_manager_factory import BaseManagerFactory

    # New (recommended)
    from aioia_core.factories.base_repository_factory import BaseRepositoryFactory
"""

from __future__ import annotations

import warnings

# Re-export from base_repository_factory module
from aioia_core.factories.base_repository_factory import (
    BaseRepositoryFactory,
    RepositoryType,
)


def __getattr__(name: str):
    """Provide deprecated aliases for backwards compatibility."""
    deprecated_mapping = {
        "BaseManagerFactory": "BaseRepositoryFactory",
        "ManagerType": "RepositoryType",
    }

    if name in deprecated_mapping:
        new_name = deprecated_mapping[name]
        warnings.warn(
            f"{name} is deprecated, use {new_name} instead. "
            "Import from aioia_core.factories.base_repository_factory instead of "
            "aioia_core.factories.base_manager_factory",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Explicit aliases for type checkers and static analysis
BaseManagerFactory = BaseRepositoryFactory
ManagerType = RepositoryType

__all__ = [
    # Deprecated aliases (backwards compatibility)
    "BaseManagerFactory",
    "ManagerType",
]
