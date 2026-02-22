"""Tests for app.domain.entities.user.User, UserRole, UserStatus."""

import unittest

from tests.common import BaseTestCase

from app.domain.entities.user import User, UserRole, UserStatus


class UserTestCase(BaseTestCase):
    """Global base class for ALL User entity tests."""

    def setUp(self) -> None:
        super().setUp()
        self.valid_user_data = {
            "id": self.test_uuid,
            "google_id": self.fake.bothify("google-########"),
            "email": self.fake.email(),
            "name": self.fake.name(),
            "picture": self.fake.image_url(),
            "role": UserRole.LOADER,
            "status": UserStatus.ACTIVE,
            "created_at": self.test_timestamp,
            "updated_at": self.test_timestamp,
        }

    def get_instance(self, **overrides: object) -> User:
        data = self.valid_user_data.copy()
        data.update(overrides)
        return User(**data)


class TestIsActive(UserTestCase):
    """Tests for is_active property."""

    def test_is_active_success_active_status(self) -> None:
        """
        When: User has ACTIVE status
        Then: Should return True
        """
        user = self.get_instance(status=UserStatus.ACTIVE)
        self.assertTrue(user.is_active)

    def test_is_active_error_pending_status(self) -> None:
        """
        When: User has PENDING status
        Then: Should return False
        """
        user = self.get_instance(status=UserStatus.PENDING)
        self.assertFalse(user.is_active)

    def test_is_active_error_disabled_status(self) -> None:
        """
        When: User has DISABLED status
        Then: Should return False
        """
        user = self.get_instance(status=UserStatus.DISABLED)
        self.assertFalse(user.is_active)


class TestIsPending(UserTestCase):
    """Tests for is_pending property."""

    def test_is_pending_success_pending_status(self) -> None:
        """
        When: User has PENDING status
        Then: Should return True
        """
        user = self.get_instance(status=UserStatus.PENDING)
        self.assertTrue(user.is_pending)

    def test_is_pending_error_active_status(self) -> None:
        """
        When: User has ACTIVE status
        Then: Should return False
        """
        user = self.get_instance(status=UserStatus.ACTIVE)
        self.assertFalse(user.is_pending)

    def test_is_pending_error_disabled_status(self) -> None:
        """
        When: User has DISABLED status
        Then: Should return False
        """
        user = self.get_instance(status=UserStatus.DISABLED)
        self.assertFalse(user.is_pending)


class TestHasRole(UserTestCase):
    """Tests for has_role() method."""

    def test_has_role_success_single_role_match(self) -> None:
        """
        When: User has LOADER role and checking for LOADER
        Then: Should return True
        """
        user = self.get_instance(role=UserRole.LOADER)
        self.assertTrue(user.has_role(UserRole.LOADER))

    def test_has_role_success_multiple_roles_match(self) -> None:
        """
        When: User has ADMIN role and checking against multiple roles
        Then: Should return True if ADMIN is in the list
        """
        user = self.get_instance(role=UserRole.ADMIN)
        self.assertTrue(user.has_role(UserRole.ADMIN, UserRole.LOADER))

    def test_has_role_error_no_match(self) -> None:
        """
        When: User has LOADER role and checking for ADMIN
        Then: Should return False
        """
        user = self.get_instance(role=UserRole.LOADER)
        self.assertFalse(user.has_role(UserRole.ADMIN))

    def test_has_role_error_none_role(self) -> None:
        """
        When: User has no role assigned (None)
        Then: Should return False for any role check
        """
        user = self.get_instance(role=None)
        self.assertFalse(user.has_role(UserRole.ADMIN))
        self.assertFalse(user.has_role(UserRole.LOADER))
        self.assertFalse(user.has_role(UserRole.APPROVER))

    def test_has_role_success_approver(self) -> None:
        """
        When: User has APPROVER role
        Then: Should match APPROVER
        """
        user = self.get_instance(role=UserRole.APPROVER)
        self.assertTrue(user.has_role(UserRole.APPROVER))

    def test_has_role_success_all_roles(self) -> None:
        """
        When: Checking against all roles
        Then: Should match if user role is any of them
        """
        user = self.get_instance(role=UserRole.ADMIN)
        self.assertTrue(user.has_role(UserRole.ADMIN, UserRole.LOADER, UserRole.APPROVER))


class TestUserRoleEnum(UserTestCase):
    """Tests for UserRole enum values."""

    def test_user_role_values(self) -> None:
        """
        When: Accessing UserRole values
        Then: Should have correct string values
        """
        self.assertEqual(UserRole.ADMIN.value, "admin")
        self.assertEqual(UserRole.LOADER.value, "loader")
        self.assertEqual(UserRole.APPROVER.value, "approver")

    def test_user_role_count(self) -> None:
        """
        When: Counting UserRole members
        Then: Should have exactly 3
        """
        self.assertEqual(len(UserRole), 3)

    def test_user_role_string_comparison(self) -> None:
        """
        When: Comparing UserRole to string
        Then: Should be equal (str mixin)
        """
        self.assertEqual(UserRole.ADMIN, "admin")


class TestUserStatusEnum(UserTestCase):
    """Tests for UserStatus enum values."""

    def test_user_status_values(self) -> None:
        """
        When: Accessing UserStatus values
        Then: Should have correct string values
        """
        self.assertEqual(UserStatus.PENDING.value, "pending")
        self.assertEqual(UserStatus.ACTIVE.value, "active")
        self.assertEqual(UserStatus.DISABLED.value, "disabled")

    def test_user_status_count(self) -> None:
        """
        When: Counting UserStatus members
        Then: Should have exactly 3
        """
        self.assertEqual(len(UserStatus), 3)


class TestUserAttributes(UserTestCase):
    """Tests for User dataclass attributes."""

    def test_user_attributes_all_set(self) -> None:
        """
        When: User is created with all attributes
        Then: Should store all values correctly
        """
        user = self.get_instance()

        self.assertEqual(user.id, self.valid_user_data["id"])
        self.assertEqual(user.google_id, self.valid_user_data["google_id"])
        self.assertEqual(user.email, self.valid_user_data["email"])
        self.assertEqual(user.name, self.valid_user_data["name"])
        self.assertEqual(user.picture, self.valid_user_data["picture"])
        self.assertEqual(user.role, UserRole.LOADER)
        self.assertEqual(user.status, UserStatus.ACTIVE)

    def test_user_attributes_optional_picture(self) -> None:
        """
        When: User is created without picture
        Then: picture should be None
        """
        user = self.get_instance(picture=None)
        self.assertIsNone(user.picture)

    def test_user_attributes_optional_role(self) -> None:
        """
        When: User is created without role (pending approval)
        Then: role should be None
        """
        user = self.get_instance(role=None)
        self.assertIsNone(user.role)
