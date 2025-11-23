"""Authentication and authorization utilities for AIoIA projects."""

from enum import Enum
from typing import Protocol

from sqlalchemy.orm import Session


class UserRole(str, Enum):
    """Standard user roles for all AIoIA projects."""

    ADMIN = "admin"
    USER = "user"


class UserRoleProvider(Protocol):
    """
    Protocol for retrieving user roles and context.

    Projects implement this to integrate their user management system
    with BaseCrudRouter's authentication/authorization.
    """

    def get_user_role(self, user_id: str, db: Session) -> UserRole | None:
        """
        Get user's role by ID.

        Args:
            user_id: User identifier
            db: Database session

        Returns:
            UserRole if user exists, None otherwise
        """
        ...

    def get_user_context(self, user_id: str, db: Session) -> dict | None:
        """
        Get user context for monitoring/observability tools.

        Args:
            user_id: User identifier
            db: Database session

        Returns:
            Dictionary with user info (id, username, email, etc.)
            None if user not found
        """
        ...
