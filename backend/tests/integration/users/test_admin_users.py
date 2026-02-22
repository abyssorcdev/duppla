"""Integration tests for admin user operations (approve, disable, list)."""

from uuid import uuid4

from app.domain.entities.user import UserRole, UserStatus
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.user_repository import UserRepository

from .conftest import create_user_in_db, fake


class TestApproveUser:
    """Verify admin user approval persists in the database."""

    def test_approve_pending_user(self, db):
        """
        When: Admin approves a pending user with a role
        Then: User status should become ACTIVE and role should be assigned
        """
        user = create_user_in_db(db)
        admin_email = fake.email()
        assert user.status == UserStatus.PENDING
        assert user.role is None

        repo = UserRepository(db)
        approved = repo.approve(user.id, UserRole.LOADER, approved_by=admin_email)

        assert approved is not None
        assert approved.status == UserStatus.ACTIVE
        assert approved.role == UserRole.LOADER

        db.expire_all()
        row = db.query(UserModel).filter_by(id=user.id).first()
        assert row.status == "active"
        assert row.role == "loader"

    def test_approve_with_admin_role(self, db):
        """
        When: User is approved as ADMIN
        Then: Role should be 'admin'
        """
        user = create_user_in_db(db)
        admin_email = fake.email()

        repo = UserRepository(db)
        approved = repo.approve(user.id, UserRole.ADMIN, approved_by=admin_email)

        assert approved.role == UserRole.ADMIN

    def test_approve_nonexistent_user(self, db):
        """
        When: User ID does not exist
        Then: Should return None
        """
        repo = UserRepository(db)
        result = repo.approve(uuid4(), UserRole.LOADER)

        assert result is None


class TestDisableUser:
    """Verify admin user disabling persists in the database."""

    def test_disable_active_user(self, db):
        """
        When: Admin disables an active user
        Then: User status should become DISABLED
        """
        user = create_user_in_db(db)
        admin_email = fake.email()

        repo = UserRepository(db)
        repo.approve(user.id, UserRole.LOADER, approved_by=admin_email)

        disabled = repo.disable(user.id, disabled_by=admin_email)

        assert disabled is not None
        assert disabled.status == UserStatus.DISABLED

        db.expire_all()
        row = db.query(UserModel).filter_by(id=user.id).first()
        assert row.status == "disabled"

    def test_disable_nonexistent_user(self, db):
        """
        When: User ID does not exist
        Then: Should return None
        """
        repo = UserRepository(db)
        result = repo.disable(uuid4())

        assert result is None


class TestListUsers:
    """Verify user listing from the database."""

    def test_list_all_users(self, db):
        """
        When: Multiple users exist
        Then: list_all should return them with correct total
        """
        for _ in range(3):
            create_user_in_db(db)

        repo = UserRepository(db)
        users, total = repo.list_all()

        assert total >= 3
        assert len(users) >= 3

    def test_list_filter_by_status(self, db):
        """
        When: Users exist with different statuses
        Then: Filtering by status should return only matching users
        """
        user1 = create_user_in_db(db)
        create_user_in_db(db)

        repo = UserRepository(db)
        repo.approve(user1.id, UserRole.LOADER)

        active_users, _ = repo.list_all(status="active")
        pending_users, _ = repo.list_all(status="pending")

        assert all(u.status == UserStatus.ACTIVE for u in active_users)
        assert all(u.status == UserStatus.PENDING for u in pending_users)

    def test_list_pagination(self, db):
        """
        When: More users exist than the limit
        Then: Should respect skip and limit parameters
        """
        for _ in range(5):
            create_user_in_db(db)

        repo = UserRepository(db)
        users, total = repo.list_all(skip=0, limit=2)

        assert len(users) == 2
        assert total >= 5
