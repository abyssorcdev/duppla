"""User SQLAlchemy model.

Maps User domain entity to users database table.
"""

from typing import ClassVar

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from app.infrastructure.database.models.base import Base


class UserModel(Base):
    """SQLAlchemy model for finance.users table.

    Attributes:
        id: UUID primary key
        google_id: Google OAuth subject ID (unique)
        email: User email (unique)
        name: Display name from Google
        picture: Avatar URL from Google
        role: Assigned role (admin, loader, approver) — null while pending
        status: Account lifecycle (pending, active, disabled)
        created_at: Registration timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"
    __table_args__: ClassVar[dict] = {"schema": "finance"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    google_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    picture = Column(String(512), nullable=True)
    role = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, server_default="pending")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
