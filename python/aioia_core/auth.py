"""Authentication and authorization utilities for AIoIA projects."""

from enum import Enum
from typing import Protocol

from pydantic import BaseModel
from sqlalchemy.orm import Session


class UserRole(str, Enum):
    """Standard user roles for all AIoIA projects."""

    ADMIN = "admin"
    USER = "user"


class UserInfo(BaseModel):
    """
    User information model.

    Combines user identity, metadata, and role information.
    Designed for authorization and monitoring/observability tools.

    Fields based on OIDC UserInfo standard:
    - sub: Subject - Unique identifier for the user
    - email: Email address
    - name: Display name
    - role: User's role in the system
    """

    sub: str
    email: str | None = None
    name: str | None = None
    role: UserRole


class UserRoleProvider(Protocol):
    """
    Protocol for retrieving user roles and context.

    Projects implement this to integrate their user management system
    with BaseCrudRouter's authentication/authorization.
    """

    def get_user_role(  # pylint: disable=unnecessary-ellipsis
        self, user_id: str, db: Session
    ) -> UserRole | None:
        """
        Get user's role by ID.

        Args:
            user_id: User identifier
            db: Database session
        """
        ...

    def get_user_context(  # pylint: disable=unnecessary-ellipsis
        self, user_id: str, db: Session
    ) -> dict | None:
        """
        Get user context for monitoring/observability tools.

        Args:
            user_id: User identifier
            db: Database session
        """
        ...
