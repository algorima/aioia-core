import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aioia_core.auth import UserRole
from aioia_core.errors import FORBIDDEN, INVALID_TOKEN
from aioia_core.fastapi import BaseCrudRouter
from aioia_core.testing.crud_fixtures import (
    Base,
    TestCreate,
    TestManager,
    TestManagerFactory,
    TestModel,
    TestUpdate,
)

SECRET = "test-secret-key"


def make_jwt(sub: str = "admin_user"):
    return jwt.encode(
        {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=10)},
        SECRET,
        algorithm="HS256",
    )


class MockUserRoleProvider:
    """Mock role provider for testing"""

    def get_user_role(self, user_id: str, db):  # pylint: disable=unused-argument
        """Return admin role for admin_user, regular role for others"""
        if user_id == "admin_user":
            return UserRole.ADMIN
        if user_id == "regular_user":
            return UserRole.USER
        return None

    def get_user_context(self, user_id: str, db):  # pylint: disable=unused-argument
        """Return user context for monitoring"""
        if user_id == "admin_user":
            return {
                "id": user_id,
                "username": "admin",
                "email": "admin@test.com",
            }
        if user_id == "regular_user":
            return {
                "id": user_id,
                "username": "user",
                "email": "user@test.com",
            }
        return None


class TestBaseCrudRouter(unittest.TestCase):
    """Test class for BaseCrudRouter with admin authorization"""

    db_path: str

    def setUp(self):
        """Set up a new DB and FastAPI app for each test."""
        # Create a temporary SQLite file that gets cleaned up automatically.
        # The 'with' statement ensures the file handle is closed properly.
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            self.db_path = temp_db.name

        # Schedule the cleanup of the temporary file.
        # This will run even if the test fails.
        self.addCleanup(Path(self.db_path).unlink, missing_ok=True)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False}
        )

        # Create tables
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        self.manager_factory = TestManagerFactory(
            repository_class=TestManager, db_session_factory=self.SessionLocal
        )
        self.role_provider = MockUserRoleProvider()

        # Create router
        self.router = BaseCrudRouter[TestModel, TestCreate, TestUpdate, TestManager](
            model_class=TestModel,
            create_schema=TestCreate,
            update_schema=TestUpdate,
            db_session_factory=self.SessionLocal,
            manager_factory=self.manager_factory,
            role_provider=self.role_provider,
            jwt_secret_key=SECRET,
            resource_name="test-items",
            tags=["TestItems"],
        ).get_router()

        # Create FastAPI app
        app = FastAPI()
        app.include_router(self.router)
        self.test_client = TestClient(app)

    def tearDown(self):
        """Drop all tables and dispose engine after each test."""
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def admin_auth_header(self):
        """Return Authorization header with admin JWT token."""
        return {"Authorization": f"Bearer {make_jwt('admin_user')}"}

    def user_auth_header(self):
        """Return Authorization header with regular user JWT token."""
        return {"Authorization": f"Bearer {make_jwt('regular_user')}"}

    def test_admin_can_access_all_endpoints(self):
        """Test that admin users can access all CRUD endpoints."""
        # Create
        resp = self.test_client.post(
            "/test-items", json={"name": "foo"}, headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        assert data is not None
        self.assertIsInstance(data["id"], str)
        self.assertEqual(data["name"], "foo")
        item_id = data["id"]
        assert item_id is not None

        # Get single item
        resp = self.test_client.get(
            f"/test-items/{item_id}", headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["name"], "foo")

        # Get list
        resp = self.test_client.get("/test-items", headers=self.admin_auth_header())
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(result["total"], 1)
        self.assertIsInstance(result["data"], list)
        assert result["data"] is not None
        self.assertEqual(result["data"][0]["id"], item_id)

        # Update
        resp = self.test_client.patch(
            f"/test-items/{item_id}",
            json={"name": "bar"},
            headers=self.admin_auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["name"], "bar")

        # Delete
        resp = self.test_client.delete(
            f"/test-items/{item_id}", headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 200)

    def check_forbidden(self, method: str, url: str, **kwargs):
        """Helper to check for 403 Forbidden responses."""
        resp = self.test_client.request(
            method, url, headers=self.user_auth_header(), **kwargs
        )
        self.assertEqual(resp.status_code, 403)
        error_details = resp.json()
        assert error_details is not None
        self.assertEqual(error_details["detail"]["code"], FORBIDDEN)
        self.assertIn("Admin access required", error_details["detail"]["detail"])

    def test_regular_user_forbidden(self):
        """Test that regular users are forbidden from accessing admin endpoints."""
        self.check_forbidden("POST", "/test-items", json={"name": "foo"})
        self.check_forbidden("GET", "/test-items")
        self.check_forbidden("GET", "/test-items/some-id")
        self.check_forbidden("PATCH", "/test-items/some-id", json={"name": "bar"})
        self.check_forbidden("DELETE", "/test-items/some-id")

    def test_no_auth_unauthorized(self):
        """Test that requests without authentication are forbidden."""
        # When no auth is provided, get_user_id_from_token returns None,
        # get_current_user_role also returns None,
        # which causes get_admin_user to raise a 403 Forbidden error.
        resp = self.test_client.get("/test-items")
        self.assertEqual(resp.status_code, 403)
        error_details = resp.json()["detail"]
        self.assertEqual(error_details["code"], FORBIDDEN)
        self.assertIn("Admin access required", error_details["detail"])

    def test_invalid_token_unauthorized(self):
        """Test that requests with invalid tokens are unauthorized."""
        resp = self.test_client.get(
            "/test-items", headers={"Authorization": "Bearer invalid-token"}
        )
        self.assertEqual(resp.status_code, 401)
        error_details = resp.json()
        assert error_details is not None
        self.assertEqual(error_details["detail"]["code"], INVALID_TOKEN)

    def test_list_with_sorting(self):
        """Test list endpoint with single and multi-field sorting."""
        auth_header = self.admin_auth_header()
        # Create items to sort
        self.test_client.post(
            "/test-items", json={"name": "charlie", "value": 10}, headers=auth_header
        )
        self.test_client.post(
            "/test-items", json={"name": "alpha", "value": 30}, headers=auth_header
        )
        self.test_client.post(
            "/test-items", json={"name": "beta", "value": 20}, headers=auth_header
        )
        self.test_client.post(
            "/test-items", json={"name": "beta", "value": 10}, headers=auth_header
        )

        # Test single field sort ascending
        resp = self.test_client.get(
            '/test-items?sort=[["name", "asc"]]', headers=auth_header
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(
            [item["name"] for item in data], ["alpha", "beta", "beta", "charlie"]
        )

        # Test single field sort descending
        resp = self.test_client.get(
            '/test-items?sort=[["value", "desc"]]', headers=auth_header
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual([item["value"] for item in data], [30, 20, 10, 10])

        # Test multi-field sorting (name asc, value desc)
        resp = self.test_client.get(
            '/test-items?sort=[["name", "asc"], ["value", "desc"]]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(
            [item["name"] for item in data], ["alpha", "beta", "beta", "charlie"]
        )
        self.assertEqual([item["value"] for item in data], [30, 20, 10, 10])

        # Test sorting with camelCase field name
        resp = self.test_client.get(
            '/test-items?sort=[["createdAt", "desc"]]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertGreater(data[0]["createdAt"], data[1]["createdAt"])

    def test_user_not_found_for_token(self):
        """Test that a 401 is raised if the user for a valid token is not found."""
        auth_header = {"Authorization": f"Bearer {make_jwt('non_existent_user')}"}
        resp = self.test_client.get("/test-items", headers=auth_header)
        self.assertEqual(resp.status_code, 401)
        error_details = resp.json()
        assert error_details is not None
        self.assertEqual(error_details["detail"]["code"], INVALID_TOKEN)
        self.assertIn(
            "User associated with token not found", error_details["detail"]["detail"]
        )

    def test_invalid_sort_param(self):
        """Test invalid sort parameter with admin auth."""
        resp = self.test_client.get(
            "/test-items?sort=notjson", headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 400)
        resp = self.test_client.get(
            "/test-items?sort=[1,2,3]", headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_filters_param(self):
        """Test invalid filters parameter with admin auth."""
        # Test case 1: filters parameter is not a valid JSON string
        resp = self.test_client.get(
            "/test-items?filters=not-a-json-string", headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 400)
        detail = resp.json()["detail"]
        self.assertEqual(detail["code"], "INVALID_QUERY_PARAMS")
        self.assertIn(
            "'filters' parameter must be a valid JSON string", detail["detail"]
        )

        # Test case 2: filters parameter is not a list after JSON parsing
        resp = self.test_client.get(
            '/test-items?filters={"key":"value"}', headers=self.admin_auth_header()
        )
        self.assertEqual(resp.status_code, 400)
        detail = resp.json()["detail"]
        self.assertEqual(detail["code"], "INVALID_QUERY_PARAMS")
        self.assertIn(
            "'filters' parameter must be a list of filter objects.", detail["detail"]
        )

    def test_list_with_filters(self):
        """Test list endpoint with various filter operators."""
        auth_header = self.admin_auth_header()
        # Create items to filter
        self.test_client.post(
            "/test-items", json={"name": "alpha", "value": 10}, headers=auth_header
        )
        self.test_client.post(
            "/test-items", json={"name": "beta", "value": 20}, headers=auth_header
        )
        self.test_client.post(
            "/test-items", json={"name": "charlie", "value": None}, headers=auth_header
        )

        # Test 'eq' filter
        resp = self.test_client.get(
            '/test-items?filters=[{"field":"name","operator":"eq","value":"alpha"}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "alpha")

        # Test 'in' filter
        resp = self.test_client.get(
            '/test-items?filters=[{"field":"name","operator":"in","value":["alpha","beta"]}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 2)

        # Test 'or' conditional filter
        resp = self.test_client.get(
            '/test-items?filters=[{"operator":"or","value":[{"field":"name","operator":"eq","value":"alpha"},{"field":"name","operator":"eq","value":"charlie"}]}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 2)
        self.assertIn(data[0]["name"], ["alpha", "charlie"])
        self.assertIn(data[1]["name"], ["alpha", "charlie"])

        # Test 'null' operator
        resp = self.test_client.get(
            '/test-items?filters=[{"field":"value","operator":"null"}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "charlie")
        self.assertIsNone(data[0]["value"])

        # Test 'nnull' operator
        resp = self.test_client.get(
            '/test-items?filters=[{"field":"value","operator":"nnull"}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 2)

        # Test filtering with camelCase field name
        resp = self.test_client.get(
            '/test-items?filters=[{"field":"value","operator":"eq","value":20}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "beta")

        # Test filtering with camelCase field name
        created_item_time = data[0]["createdAt"]
        resp = self.test_client.get(
            f'/test-items?filters=[{{"field":"createdAt","operator":"eq","value":"{created_item_time}"}}]',
            headers=auth_header,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        assert data is not None
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["createdAt"], created_item_time)


class TestCreateRepositoryDependencyFromFactory(unittest.TestCase):
    """Test class for _create_repository_dependency_from_factory method"""

    db_path: str

    def setUp(self):
        """Set up a new DB and FastAPI app for each test."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            self.db_path = temp_db.name

        self.addCleanup(Path(self.db_path).unlink, missing_ok=True)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False}
        )

        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        self.manager_factory = TestManagerFactory(
            repository_class=TestManager, db_session_factory=self.SessionLocal
        )
        self.role_provider = MockUserRoleProvider()

    def tearDown(self):
        """Drop all tables and dispose engine after each test."""
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_create_repository_dependency_from_factory(self):
        """Test that _create_repository_dependency_from_factory creates a working dependency."""
        # Create router
        crud_router = BaseCrudRouter[TestModel, TestCreate, TestUpdate, TestManager](
            model_class=TestModel,
            create_schema=TestCreate,
            update_schema=TestUpdate,
            db_session_factory=self.SessionLocal,
            repository_factory=self.manager_factory,
            role_provider=self.role_provider,
            jwt_secret_key=SECRET,
            resource_name="test-items",
            tags=["TestItems"],
        )

        # Create a secondary repository factory (simulating StudioRepositoryFactory)
        secondary_factory = TestManagerFactory(
            repository_class=TestManager, db_session_factory=self.SessionLocal
        )

        # Use _create_repository_dependency_from_factory to create dependency
        secondary_dep = crud_router._create_repository_dependency_from_factory(
            secondary_factory
        )

        # Verify the dependency is callable
        self.assertTrue(callable(secondary_dep))

    def test_repository_dependency_shares_db_session(self):
        """Test that repositories created from dependency share the same DB session."""
        # Create a custom router subclass that exposes the dependency for testing
        class TestableRouter(
            BaseCrudRouter[TestModel, TestCreate, TestUpdate, TestManager]
        ):
            def __init__(self, *args, secondary_factory, **kwargs):
                super().__init__(*args, **kwargs)
                self.get_secondary_repository_dep = (
                    self._create_repository_dependency_from_factory(secondary_factory)
                )
                self._register_test_route()

            def _register_test_route(self):
                from fastapi import Depends

                @self.router.get("/test-session-sharing")
                async def test_session_sharing(
                    primary_repo: TestManager = Depends(self.get_repository_dep),
                    secondary_repo: TestManager = Depends(
                        self.get_secondary_repository_dep
                    ),
                ):
                    # Both repositories should have the same db session
                    return {
                        "primary_session_id": id(primary_repo.db),
                        "secondary_session_id": id(secondary_repo.db),
                        "same_session": primary_repo.db is secondary_repo.db,
                    }

        secondary_factory = TestManagerFactory(
            repository_class=TestManager, db_session_factory=self.SessionLocal
        )

        router = TestableRouter(
            model_class=TestModel,
            create_schema=TestCreate,
            update_schema=TestUpdate,
            db_session_factory=self.SessionLocal,
            repository_factory=self.manager_factory,
            role_provider=self.role_provider,
            jwt_secret_key=SECRET,
            resource_name="test-items",
            tags=["TestItems"],
            secondary_factory=secondary_factory,
        ).get_router()

        app = FastAPI()
        app.include_router(router)
        test_client = TestClient(app)

        # Call the test endpoint
        resp = test_client.get("/test-session-sharing")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Verify both repositories share the same DB session
        self.assertTrue(data["same_session"])
        self.assertEqual(data["primary_session_id"], data["secondary_session_id"])


if __name__ == "__main__":
    unittest.main()
