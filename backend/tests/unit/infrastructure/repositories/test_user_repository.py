"""Tests for app.infrastructure.repositories.user_repository.UserRepository – coverage gaps."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from tests.common import BaseTestCase

from app.domain.entities.user import UserRole, UserStatus


class UserRepositoryTestCase(BaseTestCase):
    """Base class for UserRepository tests."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        with patch("app.infrastructure.repositories.user_repository.AuditRepository"):
            from app.infrastructure.repositories.user_repository import UserRepository

            self.repo = UserRepository(self.mock_db)
            self.repo._audit = MagicMock()

    def _make_db_model(self, **overrides):
        model = MagicMock()
        model.id = overrides.get("id", uuid4())
        model.google_id = overrides.get("google_id", self.fake.bothify("g-########"))
        model.email = overrides.get("email", self.fake.email())
        model.name = overrides.get("name", self.fake.name())
        model.picture = overrides.get("picture", self.fake.image_url())
        model.role = overrides.get("role", UserRole.LOADER.value)
        model.status = overrides.get("status", UserStatus.ACTIVE.value)
        model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()
        return model


class TestFindByGoogleId(UserRepositoryTestCase):
    def test_find_by_google_id_success(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model
        result = self.repo.find_by_google_id("gid")
        self.assertIsNotNone(result)

    def test_find_by_google_id_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.repo.find_by_google_id("nope")
        self.assertIsNone(result)


class TestFindById(UserRepositoryTestCase):
    def test_find_by_id_success(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model
        result = self.repo.find_by_id(db_model.id)
        self.assertIsNotNone(result)

    def test_find_by_id_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.repo.find_by_id(uuid4())
        self.assertIsNone(result)


class TestListAll(UserRepositoryTestCase):
    def test_list_all_success(self) -> None:
        mock_query = MagicMock()
        mock_query.count.return_value = 2
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            self._make_db_model(), self._make_db_model()
        ]
        self.mock_db.query.return_value = mock_query
        users, total = self.repo.list_all()
        self.assertEqual(total, 2)

    def test_list_all_with_status_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 1
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self._make_db_model()]
        self.mock_db.query.return_value = mock_query
        users, total = self.repo.list_all(status="pending")
        self.assertEqual(total, 1)


class TestCreate(UserRepositoryTestCase):
    def test_create_success(self) -> None:
        db_model = self._make_db_model(role=None, status=UserStatus.PENDING.value)
        self.mock_db.refresh.side_effect = lambda m: None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("app.infrastructure.repositories.user_repository.UserModel", return_value=db_model):
            result = self.repo.create(
                google_id=self.fake.bothify("g-########"),
                email=self.fake.email(),
                name=self.fake.name(),
                picture=None,
            )

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called()


class TestApprove(UserRepositoryTestCase):
    def test_approve_success_pending_user(self) -> None:
        db_model = self._make_db_model(role=None, status=UserStatus.PENDING.value)
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.approve(db_model.id, UserRole.LOADER, approved_by=self.fake.email())
        self.assertIsNotNone(result)
        self.mock_db.commit.assert_called()

    def test_approve_success_already_active_same_role(self) -> None:
        db_model = self._make_db_model(role=UserRole.LOADER.value, status=UserStatus.ACTIVE.value)
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.approve(db_model.id, UserRole.LOADER)
        self.assertIsNotNone(result)

    def test_approve_success_role_change(self) -> None:
        db_model = self._make_db_model(role=UserRole.LOADER.value, status=UserStatus.ACTIVE.value)
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.approve(db_model.id, UserRole.ADMIN, approved_by=self.fake.email())
        self.assertIsNotNone(result)

    def test_approve_error_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.repo.approve(uuid4(), UserRole.ADMIN)
        self.assertIsNone(result)


class TestDisable(UserRepositoryTestCase):
    def test_disable_success(self) -> None:
        db_model = self._make_db_model(status=UserStatus.ACTIVE.value)
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.disable(db_model.id, disabled_by=self.fake.email())
        self.assertIsNotNone(result)
        self.mock_db.commit.assert_called()

    def test_disable_error_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.repo.disable(uuid4())
        self.assertIsNone(result)
