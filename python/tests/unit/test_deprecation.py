"""Tests for deprecated aliases and backwards compatibility."""

from __future__ import annotations

import importlib
import sys
import unittest
import warnings


class TestDeprecationWarnings(unittest.TestCase):
    """Test that deprecated imports raise DeprecationWarning."""

    def test_base_manager_import_warning(self):
        """managers module import should raise DeprecationWarning."""
        # Remove module from cache to force fresh import
        if "aioia_core.managers" in sys.modules:
            del sys.modules["aioia_core.managers"]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Import deprecated module
            import aioia_core.managers  # noqa: F401

            # Verify warning was raised
            self.assertTrue(
                any(
                    issubclass(warn.category, DeprecationWarning)
                    and "managers module is deprecated" in str(warn.message)
                    for warn in w
                ),
                "managers module import should raise DeprecationWarning",
            )

    def test_base_manager_factory_import_warning(self):
        """base_manager_factory module import should raise DeprecationWarning."""
        # Remove module from cache to force fresh import
        if "aioia_core.factories.base_manager_factory" in sys.modules:
            del sys.modules["aioia_core.factories.base_manager_factory"]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            import aioia_core.factories.base_manager_factory  # noqa: F401

            self.assertTrue(
                any(
                    issubclass(warn.category, DeprecationWarning)
                    and "base_manager_factory module is deprecated" in str(warn.message)
                    for warn in w
                ),
                "base_manager_factory module import should raise DeprecationWarning",
            )

    def test_manager_factory_parameter_warning(self):
        """BaseCrudRouter with manager_factory parameter should raise DeprecationWarning."""
        from pydantic import BaseModel
        from sqlalchemy.orm import sessionmaker
        from aioia_core.fastapi import BaseCrudRouter
        from aioia_core.factories import BaseRepositoryFactory

        class DummyModel(BaseModel):
            id: str

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Create mock factory
            mock_session_factory = sessionmaker()
            mock_repository_factory = object()  # Simple mock

            # Use deprecated parameter
            try:
                router = BaseCrudRouter(
                    model_class=DummyModel,
                    create_schema=DummyModel,
                    update_schema=DummyModel,
                    db_session_factory=mock_session_factory,
                    role_provider=None,
                    jwt_secret_key=None,
                    resource_name="test",
                    tags=["test"],
                    manager_factory=mock_repository_factory,  # Deprecated parameter
                )
            except Exception:
                # Router initialization might fail due to mock objects, but we only care about the warning
                pass

            self.assertTrue(
                any(
                    issubclass(warn.category, DeprecationWarning)
                    and "manager_factory parameter is deprecated" in str(warn.message)
                    for warn in w
                ),
                "manager_factory parameter should raise DeprecationWarning",
            )


if __name__ == "__main__":
    unittest.main()
