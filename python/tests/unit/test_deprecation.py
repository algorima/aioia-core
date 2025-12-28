"""Tests for deprecated aliases and backwards compatibility."""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aioia_core.fastapi import BaseCrudRouter
from aioia_core.testing.crud_fixtures import (
    Base,
    TestCreate,
    TestModel,
    TestRepository,
    TestRepositoryFactory,
    TestUpdate,
)


class TestDeprecationWarnings(unittest.TestCase):
    """Test that deprecated imports raise DeprecationWarning."""

    def test_base_manager_import_warning(self):
        """managers module import should raise DeprecationWarning."""
        # Remove module from cache to force fresh import
        if "aioia_core.managers" in sys.modules:
            del sys.modules["aioia_core.managers"]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Import deprecated module using importlib
            importlib.import_module("aioia_core.managers")

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

            # Import deprecated module using importlib
            importlib.import_module("aioia_core.factories.base_manager_factory")

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

        class DummyModel(BaseModel):
            id: str

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Create mock factory
            mock_session_factory = sessionmaker()
            mock_repository_factory = object()  # Simple mock

            # Use deprecated parameter
            try:
                BaseCrudRouter(
                    model_class=DummyModel,
                    create_schema=DummyModel,
                    update_schema=DummyModel,
                    db_session_factory=mock_session_factory,
                    user_info_provider=None,
                    jwt_secret_key=None,
                    resource_name="test",
                    tags=["test"],
                    manager_factory=mock_repository_factory,  # Deprecated parameter
                )
            except (TypeError, AttributeError):
                # Router initialization might fail due to mock objects,
                # but we only care about the warning
                pass

            self.assertTrue(
                any(
                    issubclass(warn.category, DeprecationWarning)
                    and "manager_factory parameter is deprecated" in str(warn.message)
                    for warn in w
                ),
                "manager_factory parameter should raise DeprecationWarning",
            )

    def test_get_manager_dep_deprecated_alias(self):
        """Accessing get_manager_dep should raise DeprecationWarning and work as alias."""

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            db_path = temp_db.name

        try:
            engine = create_engine(
                f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
            )
            Base.metadata.create_all(engine)
            session_factory = sessionmaker(bind=engine)
            repository_factory = TestRepositoryFactory(
                repository_class=TestRepository, db_session_factory=session_factory
            )

            # Create router instance (not calling .get_router() to keep instance)
            router = BaseCrudRouter[TestModel, TestCreate, TestUpdate, TestRepository](
                model_class=TestModel,
                create_schema=TestCreate,
                update_schema=TestUpdate,
                db_session_factory=session_factory,
                repository_factory=repository_factory,
                user_info_provider=None,
                jwt_secret_key=None,
                resource_name="test",
                tags=["test"],
            )

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                # Access deprecated attribute
                manager_dep = router.get_manager_dep

                # Should raise DeprecationWarning
                self.assertTrue(
                    any(
                        issubclass(warn.category, DeprecationWarning)
                        and "get_manager_dep is deprecated" in str(warn.message)
                        for warn in w
                    ),
                    "get_manager_dep should raise DeprecationWarning",
                )

                # Should be the same as get_repository_dep (alias)
                self.assertEqual(
                    manager_dep,
                    router.get_repository_dep,
                    "get_manager_dep should be an alias for get_repository_dep",
                )

        finally:
            Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
