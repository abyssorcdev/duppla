"""User repository.

Handles all database operations for user persistence.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.user import User, UserRole, UserStatus
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.audit_repository import AuditRepository


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._audit = AuditRepository(db)

    # ── Mapping ──────────────────────────────────────────────────────────────

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            google_id=model.google_id,
            email=model.email,
            name=model.name,
            picture=model.picture,
            role=UserRole(model.role) if model.role else None,
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # ── Queries ───────────────────────────────────────────────────────────────

    def find_by_google_id(self, google_id: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.google_id == google_id).first()
        return self._to_entity(model) if model else None

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def list_all(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[User], int]:
        query = self.db.query(UserModel)
        if status:
            query = query.filter(UserModel.status == status)
        total = query.count()
        models = query.order_by(UserModel.created_at.desc()).offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models], total

    # ── Mutations ─────────────────────────────────────────────────────────────

    def create(
        self,
        google_id: str,
        email: str,
        name: str,
        picture: Optional[str] = None,
    ) -> User:
        model = UserModel(
            id=uuid.uuid4(),
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
            role=None,
            status=UserStatus.PENDING.value,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        user = self._to_entity(model)
        self._audit.log_created("users", str(user.id), f"email={user.email}", user_id="system")
        return user

    def approve(self, user_id: uuid.UUID, role: UserRole, approved_by: Optional[str] = None) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None
        old_role = model.role
        old_status = model.status
        model.role = role.value
        model.status = UserStatus.ACTIVE.value
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        user = self._to_entity(model)
        if old_status != UserStatus.ACTIVE.value:
            self._audit.log_state_change(
                "users", str(user_id), old_status, UserStatus.ACTIVE.value, user_id=approved_by
            )
        if old_role != role.value:
            self._audit.log_field_updated(
                "users",
                str(user_id),
                f"role: {old_role or 'none'}",
                f"role: {role.value}",
                user_id=approved_by,
            )
        return user

    def disable(self, user_id: uuid.UUID, disabled_by: Optional[str] = None) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None
        old_status = model.status
        model.status = UserStatus.DISABLED.value
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        user = self._to_entity(model)
        self._audit.log_state_change("users", str(user_id), old_status, UserStatus.DISABLED.value, user_id=disabled_by)
        return user
