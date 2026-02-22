"""Admin routes.

User management endpoints, restricted to admin role.
  GET   /admin/users          → list all users (filterable by status)
  PATCH /admin/users/{id}     → approve user (assign role + activate)
  PATCH /admin/users/{id}/disable → disable user
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_database
from app.api.middleware.jwt_auth import require_admin
from app.application.dtos.auth_dtos import (
    ApproveUserRequest,
    AuditLogListResponse,
    AuditLogResponse,
    UserListResponse,
    UserResponse,
)
from app.infrastructure.repositories.audit_repository import AuditRepository
from app.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_repo(db: Session = Depends(get_database)) -> UserRepository:
    return UserRepository(db)


def _get_audit_repo(db: Session = Depends(get_database)) -> AuditRepository:
    return AuditRepository(db)


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List all users",
    dependencies=[Depends(require_admin())],
)
async def list_users(
    status: Optional[str] = Query(None, description="Filter by status: pending, active, disabled"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    repo: UserRepository = Depends(_get_repo),
) -> UserListResponse:
    """List all registered users. Admin only."""
    users, total = repo.list_all(status=status, skip=skip, limit=limit)
    return UserListResponse(
        items=[
            UserResponse(
                id=u.id,
                email=u.email,
                name=u.name,
                picture=u.picture,
                role=u.role,
                status=u.status,
            )
            for u in users
        ],
        total=total,
    )


@router.patch(
    "/users/{user_id}/approve",
    response_model=UserResponse,
    summary="Approve a pending user and assign role",
    dependencies=[Depends(require_admin())],
)
async def approve_user(
    user_id: uuid.UUID,
    body: ApproveUserRequest,
    repo: UserRepository = Depends(_get_repo),
) -> UserResponse:
    """Grant access to a pending user by assigning a role. Admin only."""
    user = repo.approve(user_id, body.role)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    logger.info("Admin approved user %s with role %s", user.email, user.role)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        role=user.role,
        status=user.status,
    )


@router.patch(
    "/users/{user_id}/disable",
    response_model=UserResponse,
    summary="Disable a user",
    dependencies=[Depends(require_admin())],
)
async def disable_user(
    user_id: uuid.UUID,
    repo: UserRepository = Depends(_get_repo),
) -> UserResponse:
    """Revoke a user's access. Admin only."""
    user = repo.disable(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    logger.info("Admin disabled user %s", user.email)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        role=user.role,
        status=user.status,
    )


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    summary="List system audit logs",
    dependencies=[Depends(require_admin())],
)
async def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter: created, state_change, field_updated"),
    table_name: Optional[str] = Query(None, description="Filter by table: documents, jobs, users"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    audit_repo: AuditRepository = Depends(_get_audit_repo),
) -> AuditLogListResponse:
    """Return recent audit log entries across all tables. Admin only."""
    entries, total = audit_repo.list_recent(skip=skip, limit=limit, action=action, table_name=table_name)
    return AuditLogListResponse(
        items=[
            AuditLogResponse(
                id=e.id,
                table_name=e.table_name,
                record_id=e.record_id,
                action=e.action,
                old_value=e.old_value,
                new_value=e.new_value,
                timestamp=e.timestamp,
                user_id=e.user_id,
            )
            for e in entries
        ],
        total=total,
    )
