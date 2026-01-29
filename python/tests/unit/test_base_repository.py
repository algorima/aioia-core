from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from aioia_core.repositories import BaseRepository
from aioia_core.types import CrudFilter
from aioia_core.models import BaseModel as DBBaseModel
from aioia_core.testing.database_manager import TestDatabaseManager


# 테스트용 모델 정의
class TestModel(BaseModel):
    """테스트용 Pydantic 모델"""

    id: Optional[str] = None  # pylint: disable=consider-alternative-union-syntax
    title: str
    content: str
    created_at: Optional[  # pylint: disable=consider-alternative-union-syntax
        datetime
    ] = None
    updated_at: Optional[  # pylint: disable=consider-alternative-union-syntax
        datetime
    ] = None


class DBTestModel(DBBaseModel):
    """테스트용 SQLAlchemy 모델"""

    __tablename__ = "test_repository_models"

    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


def convert_db_model_to_model(db_model: DBTestModel) -> TestModel:
    """DB 모델을 Pydantic 모델로 변환"""
    return TestModel(
        id=db_model.id,
        title=db_model.title,
        content=db_model.content,
        created_at=db_model.created_at.replace(tzinfo=timezone.utc),
        updated_at=db_model.updated_at.replace(tzinfo=timezone.utc),
    )


def convert_model_to_db_model(model: TestModel) -> dict[str, Any]:
    """Pydantic 모델을 DB 모델 데이터로 변환"""
    return {
        "title": model.title,
        "content": model.content,
    }


class TestBaseRepository(TestDatabaseManager):
    """BaseRepository 클래스에 대한 단위 테스트"""

    @classmethod
    def setUpClass(cls) -> None:
        """테스트 클래스 설정"""
        super().setUpClass()

    def setUp(self):
        """테스트 환경 설정"""
        super().setUp()
        # BaseRepository 인스턴스 생성
        self.repository = BaseRepository[TestModel, DBTestModel, TestModel, TestModel](
            db_session=self.session,
            db_model=DBTestModel,
            convert_to_model=convert_db_model_to_model,
            convert_to_db_model=convert_model_to_db_model,
        )

    def test_create(self):
        """create 메서드 테스트"""
        # 테스트 데이터 생성
        test_model = TestModel(title="테스트 제목", content="테스트 내용")

        # 모델 생성
        created_model = self.repository.create(test_model)

        # 검증
        assert created_model.id is not None, "생성된 모델의 ID가 None입니다"
        self.assertEqual(created_model.title, "테스트 제목")
        self.assertEqual(created_model.content, "테스트 내용")
        self.assertIsNotNone(created_model.created_at)
        self.assertIsNotNone(created_model.updated_at)

        # DB에서 직접 조회하여 검증
        db_model = (
            self.session.query(DBTestModel).filter_by(id=created_model.id).first()
        )
        self.assertIsNotNone(db_model)
        self.assertEqual(db_model.title, "테스트 제목")
        self.assertEqual(db_model.content, "테스트 내용")

    def test_get_by_id(self):
        """get_by_id 메서드 테스트"""
        # 테스트 데이터 생성
        test_model = TestModel(title="테스트 제목", content="테스트 내용")
        created_model = self.repository.create(test_model)
        assert created_model.id is not None, "생성된 모델의 ID가 None입니다"

        # ID로 조회
        retrieved_model = self.repository.get_by_id(created_model.id)

        # 검증
        self.assertIsNotNone(retrieved_model)
        assert retrieved_model is not None, "조회된 모델이 None입니다"
        self.assertEqual(retrieved_model.id, created_model.id)
        self.assertEqual(retrieved_model.title, "테스트 제목")
        self.assertEqual(retrieved_model.content, "테스트 내용")

        # 존재하지 않는 ID로 조회
        non_existent_id = str(uuid4())
        non_existent_model = self.repository.get_by_id(non_existent_id)
        self.assertIsNone(non_existent_model)

    def test_update(self):
        """update 메서드 테스트"""
        # 테스트 데이터 생성
        test_model = TestModel(title="테스트 제목", content="테스트 내용")
        created_model = self.repository.create(test_model)
        assert created_model.id is not None, "생성된 모델의 ID가 None입니다"

        # 업데이트 데이터 생성
        update_model = TestModel(title="수정된 제목", content="수정된 내용")

        # 업데이트
        updated_model = self.repository.update(created_model.id, update_model)

        # 검증
        self.assertIsNotNone(updated_model)
        assert updated_model is not None, "업데이트된 모델이 None입니다"
        self.assertEqual(updated_model.id, created_model.id)
        self.assertEqual(updated_model.title, "수정된 제목")
        self.assertEqual(updated_model.content, "수정된 내용")

        # DB에서 직접 조회하여 검증
        db_model = (
            self.session.query(DBTestModel).filter_by(id=created_model.id).first()
        )
        self.assertEqual(db_model.title, "수정된 제목")
        self.assertEqual(db_model.content, "수정된 내용")

        # 존재하지 않는 ID로 업데이트
        non_existent_id = str(uuid4())
        non_existent_update = self.repository.update(non_existent_id, update_model)
        self.assertIsNone(non_existent_update)

    def test_delete(self):
        """delete 메서드 테스트"""
        # 테스트 데이터 생성
        test_model = TestModel(title="테스트 제목", content="테스트 내용")
        created_model = self.repository.create(test_model)
        assert created_model.id is not None, "생성된 모델의 ID가 None입니다"

        # 삭제
        delete_result = self.repository.delete(created_model.id)

        # 검증
        self.assertTrue(delete_result)

        # DB에서 직접 조회하여 검증
        db_model = (
            self.session.query(DBTestModel).filter_by(id=created_model.id).first()
        )
        self.assertIsNone(db_model)

        # 존재하지 않는 ID로 삭제
        non_existent_id = str(uuid4())
        non_existent_delete = self.repository.delete(non_existent_id)
        self.assertFalse(non_existent_delete)

    def test_get_all(self):
        """get_all 메서드 테스트"""
        # 테스트 데이터 생성
        for i in range(15):
            test_model = TestModel(title=f"제목 {i}", content=f"내용 {i}")
            self.repository.create(test_model)

        # 페이지네이션 테스트
        items, total = self.repository.get_all(current=1, page_size=10)
        self.assertEqual(len(items), 10)
        self.assertEqual(total, 15)

        items, total = self.repository.get_all(current=2, page_size=10)
        self.assertEqual(len(items), 5)
        self.assertEqual(total, 15)

        # 정렬 테스트
        items, _ = self.repository.get_all(sort=[("title", "asc")])
        self.assertEqual(items[0].title, "제목 0")

        items, _ = self.repository.get_all(sort=[("title", "desc")])
        self.assertEqual(items[0].title, "제목 9")

        # 필터 테스트
        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "eq", "value": "제목 5"}]
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "제목 5")

        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "contains", "value": "제목"}]
        )
        self.assertEqual(total, 15)

        items, total = self.repository.get_all(
            filters=[
                {"field": "title", "operator": "contains", "value": "제목"},
                {"field": "content", "operator": "contains", "value": "내용 1"},
            ]
        )
        self.assertEqual(total, 6)  # 내용 1, 10, 11, 12, 13, 14

    def test_filter_operators(self):
        """다양한 필터 연산자 테스트"""
        # 테스트 데이터 생성
        test_models = [
            TestModel(title="제목 A", content="내용 1"),
            TestModel(title="제목 B", content="내용 2"),
            TestModel(title="제목 C", content="내용 3"),
            TestModel(title="다른 제목", content="내용 4"),
        ]

        for model in test_models:
            self.repository.create(model)

        # eq (equals) 연산자 테스트
        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "eq", "value": "제목 A"}]
        )
        self.assertEqual(total, 1)
        self.assertEqual(items[0].title, "제목 A")

        # ne (not equals) 연산자 테스트
        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "ne", "value": "제목 A"}]
        )
        self.assertEqual(total, 3)
        self.assertNotIn("제목 A", [item.title for item in items])

        # contains 연산자 테스트
        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "contains", "value": "제목"}]
        )
        self.assertEqual(total, 4)

        # startswith 연산자 테스트
        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "startswith", "value": "제목"}]
        )
        self.assertEqual(total, 3)

        # endswith 연산자 테스트
        items, total = self.repository.get_all(
            filters=[{"field": "title", "operator": "endswith", "value": "A"}]
        )
        self.assertEqual(total, 1)
        self.assertEqual(items[0].title, "제목 A")

    def test_conditional_filters(self):
        """OR 및 중첩 조건 필터 테스트"""
        # 테스트 데이터 생성
        test_models = [
            TestModel(title="Apple", content="Red fruit"),
            TestModel(title="Banana", content="Yellow fruit"),
            TestModel(title="Carrot", content="Orange vegetable"),
            TestModel(title="Apple", content="Green fruit"),
        ]
        for model in test_models:
            self.repository.create(model)

        # OR 조건 테스트
        # title이 'Apple' 이거나 content가 'Yellow fruit'인 경우
        or_filters: list[CrudFilter] = [
            {
                "operator": "or",
                "value": [
                    {"field": "title", "operator": "eq", "value": "Apple"},
                    {"field": "content", "operator": "eq", "value": "Yellow fruit"},
                ],
            }
        ]
        items, total = self.repository.get_all(filters=or_filters)
        self.assertEqual(total, 3)
        titles = {item.title for item in items}
        self.assertIn("Apple", titles)
        self.assertIn("Banana", titles)

        # AND와 OR 중첩 조건 테스트
        # (title이 'Apple' AND content가 'Red fruit') OR (title이 'Banana')
        nested_filters: list[CrudFilter] = [
            {
                "operator": "or",
                "value": [
                    {
                        "operator": "and",
                        "value": [
                            {"field": "title", "operator": "eq", "value": "Apple"},
                            {
                                "field": "content",
                                "operator": "eq",
                                "value": "Red fruit",
                            },
                        ],
                    },
                    {"field": "title", "operator": "eq", "value": "Banana"},
                ],
            }
        ]
        items, total = self.repository.get_all(filters=nested_filters)
        self.assertEqual(total, 2)
        retrieved_titles = {item.title for item in items}
        self.assertEqual(retrieved_titles, {"Apple", "Banana"})
        # Red fruit Apple만 필터링되었는지 확인
        apple_items = [
            item
            for item in items
            if item.title == "Apple" and item.content == "Red fruit"
        ]
        self.assertEqual(len(apple_items), 1)


if __name__ == "__main__":
    unittest.main()
