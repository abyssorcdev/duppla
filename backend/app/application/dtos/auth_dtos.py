"""DTOs for authentication and user management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.domain.entities.user import UserRole, UserStatus


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    picture: Optional[str]
    role: Optional[UserRole]
    status: UserStatus

    model_config = {"from_attributes": True}


class ApproveUserRequest(BaseModel):
    role: UserRole


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int


class AuditLogResponse(BaseModel):
    id: int
    table_name: str
    record_id: str
    action: str
    old_value: Optional[str]
    new_value: Optional[str]
    timestamp: datetime
    user_id: Optional[str]

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
