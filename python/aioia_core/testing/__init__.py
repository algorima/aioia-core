"""Testing utilities for AIoIA projects."""

from aioia_core.testing.crud_fixtures import (
    TestCreate,
    TestDBModel,
    TestManager,
    TestManagerFactory,
    TestModel,
    TestUpdate,
    create_test_manager_factory,
    setup_test_database,
)
from aioia_core.testing.database_manager import TestDatabaseManager

__all__ = [
    "TestDatabaseManager",
    "TestModel",
    "TestDBModel",
    "TestCreate",
    "TestUpdate",
    "TestManager",
    "TestManagerFactory",
    "setup_test_database",
    "create_test_manager_factory",
]
