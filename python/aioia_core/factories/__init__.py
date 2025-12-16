"""Factory patterns for AIoIA projects."""

# Deprecated alias for backwards compatibility
from aioia_core.factories.base_manager_factory import BaseManagerFactory
from aioia_core.factories.base_repository_factory import BaseRepositoryFactory

__all__ = [
    # New name (recommended)
    "BaseRepositoryFactory",
    # Deprecated alias (backwards compatibility)
    "BaseManagerFactory",
]
