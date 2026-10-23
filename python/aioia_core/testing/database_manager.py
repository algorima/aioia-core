"""
Deprecated: Use aioia_core.testing.database_test_case instead.

This module provides a backwards compatibility alias for the renamed test base
class. TestDatabaseManager was renamed to DatabaseTestCase because it is a
unittest.TestCase that sets up a test database, not a repository.

Migration guide:
    # Old (deprecated)
    from aioia_core.testing.database_manager import TestDatabaseManager

    # New (recommended)
    from aioia_core.testing import DatabaseTestCase
"""

from __future__ import annotations

import warnings

from aioia_core.testing.database_test_case import DatabaseTestCase

# Issue deprecation warning when module is imported
warnings.warn(
    "aioia_core.testing.database_manager module is deprecated. "
    "Use aioia_core.testing.database_test_case instead "
    "(TestDatabaseManager -> DatabaseTestCase)",
    DeprecationWarning,
    stacklevel=2,
)

# Explicit alias for type checkers and static analysis
TestDatabaseManager = DatabaseTestCase

__all__ = [
    "TestDatabaseManager",
    "DatabaseTestCase",
]
