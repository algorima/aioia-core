"""Testing utilities for AIoIA projects."""

from __future__ import annotations

import warnings
from typing import Any

from aioia_core.testing.crud_fixtures import (
    TestCreate,
    TestDBModel,
    TestModel,
    TestRepository,
    TestRepositoryFactory,
    TestUpdate,
)
from aioia_core.testing.database_test_case import DatabaseTestCase

__all__ = [
    "DatabaseTestCase",
    "TestModel",
    "TestDBModel",
    "TestCreate",
    "TestUpdate",
    "TestRepository",
    "TestRepositoryFactory",
]

# Deprecated names for lazy loading via __getattr__ (old -> new)
_DEPRECATED_NAMES = {
    "TestDatabaseManager": "DatabaseTestCase",
    "TestManager": "TestRepository",
    "TestManagerFactory": "TestRepositoryFactory",
}


def __getattr__(name: str) -> Any:
    """PEP 562-style lazy loading of deprecated names."""
    if name in _DEPRECATED_NAMES:
        new_name = _DEPRECATED_NAMES[name]
        warnings.warn(
            f"{name} is deprecated, use {new_name} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new_name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """PEP 562-style module directory including deprecated names."""
    return list(__all__) + list(_DEPRECATED_NAMES)
