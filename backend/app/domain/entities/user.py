"""User domain entity.

Represents a system user with role-based access control.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class UserRole(str, Enum):
    ADMIN = "admin"
    LOADER = "loader"
    APPROVER = "approver"


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass
class User:
    """User entity with role and approval status.

    Attributes:
        id: UUID primary key
        google_id: Google OAuth subject identifier
        email: User email (unique)
        name: Display name
        picture: Avatar URL from Google
        role: Assigned role (None = awaiting approval)
        status: Account status
        created_at: Registration timestamp
        updated_at: Last update timestamp
    """

    id: UUID
    google_id: str
    email: str
    name: str
    picture: Optional[str]
    role: Optional[UserRole]
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @property
    def is_pending(self) -> bool:
        return self.status == UserStatus.PENDING

    def has_role(self, *roles: UserRole) -> bool:
        return self.role in roles
