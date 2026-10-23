"""Tests for DatabaseTestCase and its deprecated TestDatabaseManager alias."""

from __future__ import annotations

import importlib
import sys
import unittest
import warnings

from sqlalchemy import text

from aioia_core import testing
from aioia_core.testing import DatabaseTestCase


class TestDatabaseTestCase(DatabaseTestCase):
    """DatabaseTestCase provides an isolated session per test."""

    def test_session_is_bound_to_in_memory_sqlite(self):
        result = self.session.execute(text("SELECT 1")).scalar()
        self.assertEqual(result, 1)

    def test_session_uses_savepoint_join_mode(self):
        assert self.session is not None
        self.assertEqual(self.session.join_transaction_mode, "create_savepoint")


class TestDeprecatedTestDatabaseManager(unittest.TestCase):
    """The old name keeps working and warns."""

    def test_database_manager_module_import_warning(self):
        if "aioia_core.testing.database_manager" in sys.modules:
            del sys.modules["aioia_core.testing.database_manager"]

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            module = importlib.import_module("aioia_core.testing.database_manager")

        self.assertTrue(
            any(
                issubclass(warn.category, DeprecationWarning)
                and "database_manager module is deprecated" in str(warn.message)
                for warn in caught
            ),
            "database_manager module import should raise DeprecationWarning",
        )
        self.assertIs(module.TestDatabaseManager, DatabaseTestCase)

    def test_testing_package_lazy_alias_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            alias = testing.TestDatabaseManager

        self.assertIs(alias, DatabaseTestCase)
        self.assertTrue(
            any(
                issubclass(warn.category, DeprecationWarning)
                and "TestDatabaseManager is deprecated" in str(warn.message)
                for warn in caught
            ),
            "aioia_core.testing.TestDatabaseManager should raise DeprecationWarning",
        )

    def test_testing_package_lazy_crud_aliases_warn(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            manager = testing.TestManager
            factory = testing.TestManagerFactory

        self.assertIs(manager, testing.TestRepository)
        self.assertIs(factory, testing.TestRepositoryFactory)
        messages = [str(warn.message) for warn in caught]
        self.assertTrue(any("TestManager is deprecated" in m for m in messages))
        self.assertTrue(any("TestManagerFactory is deprecated" in m for m in messages))

    def test_new_names_do_not_warn(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = (
                testing.DatabaseTestCase,
                testing.TestRepository,
                testing.TestRepositoryFactory,
            )

        self.assertEqual(
            [w for w in caught if issubclass(w.category, DeprecationWarning)], []
        )

    def test_unknown_attribute_raises(self):
        with self.assertRaises(AttributeError):
            _ = testing.DoesNotExist


if __name__ == "__main__":
    unittest.main()
