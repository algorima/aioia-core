"""
Backwards compatibility test for BaseManager → BaseRepository rename.

This test file verifies that the deprecated BaseManager alias works correctly.
Full functionality tests are in test_base_repository.py.
"""

from __future__ import annotations

import importlib
import sys
import unittest
import warnings

from aioia_core.repositories import BaseRepository


class TestBaseManagerAlias(unittest.TestCase):
    """Test that BaseManager is an alias for BaseRepository."""

    def test_base_manager_is_base_repository_alias(self):
        """BaseManager should be the same class as BaseRepository."""
        # Remove from cache to get fresh import
        if "aioia_core.managers" in sys.modules:
            del sys.modules["aioia_core.managers"]

        # Suppress warning for this specific import
        # (warning is already tested in test_deprecation.py)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            managers_module = importlib.import_module("aioia_core.managers")

        # Verify alias
        self.assertIs(
            managers_module.BaseManager,
            BaseRepository,
            "BaseManager should be an alias for BaseRepository",
        )


if __name__ == "__main__":
    unittest.main()
