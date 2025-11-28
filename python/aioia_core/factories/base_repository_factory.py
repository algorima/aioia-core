from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.orm import Session, sessionmaker

from aioia_core.protocols import DatabaseRepositoryProtocol

# RepositoryType을 DatabaseRepositoryProtocol에 바인딩
RepositoryType = TypeVar("RepositoryType", bound=DatabaseRepositoryProtocol)


class BaseRepositoryFactory(ABC, Generic[RepositoryType]):
    """
    기본 레포지토리 팩토리 클래스

    이 클래스는 데이터베이스 저장소를 사용하는 레포지토리 인스턴스를 생성하기 위한
    기본 팩토리 패턴을 구현합니다.

    Args:
        db_session_factory: SQLAlchemy 세션 팩토리
        repository_class: 생성할 레포지토리 클래스
    """

    def __init__(
        self,
        db_session_factory: sessionmaker,
        repository_class: type[RepositoryType],
    ):
        """
        BaseRepositoryFactory 초기화

        Args:
            db_session_factory: SQLAlchemy 세션 팩토리
            repository_class: 생성할 레포지토리 클래스
        """
        self.db_session_factory = db_session_factory
        self.repository_class = repository_class

    def create_repository(self, db_session: Session | None = None) -> RepositoryType:
        """
        레포지토리 인스턴스를 생성합니다.

        이 메서드는 레포지토리 클래스의 인스턴스를 생성하고 반환합니다.
        db_session이 제공되지 않은 경우 새로운 세션을 생성합니다.

        Args:
            db_session: 선택적 데이터베이스 세션. None인 경우 새로운 세션을 생성합니다.

        Returns:
            생성된 레포지토리 인스턴스
        """
        session = db_session if db_session is not None else self.db_session_factory()
        return self.repository_class(session)

    # Deprecated alias for backwards compatibility
    def create_manager(self, db_session: Session | None = None) -> RepositoryType:
        """
        Deprecated: Use create_repository() instead.

        This method is kept for backwards compatibility with existing code
        that uses the old BaseManagerFactory interface.
        """
        return self.create_repository(db_session)
