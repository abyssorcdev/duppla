"""Tests for app.application.dtos.auth_dtos."""

from datetime import datetime
from uuid import uuid4

from tests.common import BaseTestCase

from app.application.dtos.auth_dtos import (
    ApproveUserRequest,
    AuditLogListResponse,
    AuditLogResponse,
    UserListResponse,
    UserResponse,
)
from app.domain.entities.user import UserRole, UserStatus


class TestUserResponse(BaseTestCase):
    """Tests for UserResponse DTO."""

    def test_user_response_success_valid_data(self) -> None:
        uid = uuid4()
        resp = UserResponse(
            id=uid,
            email=self.fake.email(),
            name=self.fake.name(),
            picture=self.fake.image_url(),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        self.assertEqual(resp.id, uid)
        self.assertEqual(resp.role, UserRole.ADMIN)
        self.assertEqual(resp.status, UserStatus.ACTIVE)

    def test_user_response_success_optional_picture_none(self) -> None:
        resp = UserResponse(
            id=uuid4(),
            email=self.fake.email(),
            name=self.fake.name(),
            picture=None,
            role=None,
            status=UserStatus.PENDING,
        )
        self.assertIsNone(resp.picture)
        self.assertIsNone(resp.role)


class TestApproveUserRequest(BaseTestCase):
    """Tests for ApproveUserRequest DTO."""

    def test_approve_user_request_success_valid_role(self) -> None:
        req = ApproveUserRequest(role=UserRole.LOADER)
        self.assertEqual(req.role, UserRole.LOADER)

    def test_approve_user_request_success_all_roles(self) -> None:
        for role in UserRole:
            req = ApproveUserRequest(role=role)
            self.assertEqual(req.role, role)


class TestUserListResponse(BaseTestCase):
    """Tests for UserListResponse DTO."""

    def test_user_list_response_success_with_items(self) -> None:
        items = [
            UserResponse(
                id=uuid4(),
                email=self.fake.email(),
                name=self.fake.name(),
                picture=None,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
            )
        ]
        resp = UserListResponse(items=items, total=1)
        self.assertEqual(len(resp.items), 1)
        self.assertEqual(resp.total, 1)

    def test_user_list_response_success_empty(self) -> None:
        resp = UserListResponse(items=[], total=0)
        self.assertEqual(len(resp.items), 0)


class TestAuditLogResponse(BaseTestCase):
    """Tests for AuditLogResponse DTO."""

    def test_audit_log_response_success_full(self) -> None:
        now = datetime.utcnow()
        resp = AuditLogResponse(
            id=self.fake.random_int(),
            table_name="documents",
            record_id=str(self.fake.random_int()),
            action="created",
            old_value="draft",
            new_value="pending",
            timestamp=now,
            user_id=self.fake.email(),
        )
        self.assertEqual(resp.action, "created")
        self.assertEqual(resp.old_value, "draft")

    def test_audit_log_response_success_optional_none(self) -> None:
        resp = AuditLogResponse(
            id=1,
            table_name="jobs",
            record_id="abc",
            action="state_change",
            old_value=None,
            new_value=None,
            timestamp=datetime.utcnow(),
            user_id=None,
        )
        self.assertIsNone(resp.old_value)
        self.assertIsNone(resp.user_id)


class TestAuditLogListResponse(BaseTestCase):
    """Tests for AuditLogListResponse DTO."""

    def test_audit_log_list_response_success(self) -> None:
        items = [
            AuditLogResponse(
                id=1,
                table_name="documents",
                record_id="1",
                action="created",
                old_value=None,
                new_value="created doc",
                timestamp=datetime.utcnow(),
                user_id=None,
            )
        ]
        resp = AuditLogListResponse(items=items, total=1)
        self.assertEqual(resp.total, 1)
        self.assertEqual(len(resp.items), 1)
