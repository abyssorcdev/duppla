"""Audit log SQLAlchemy model.

Generic audit table that tracks changes across all tables (documents, jobs, users).
Uses (table_name, record_id) instead of a foreign key to a specific table.
"""

from typing import ClassVar

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.infrastructure.database.models.base import Base


class AuditLogModel(Base):
    """SQLAlchemy model for finance.audit_logs.

    Attributes:
        id: Primary key
        table_name: Name of the affected table (documents, jobs, users)
        record_id: ID of the affected record (stored as string to support int and UUID)
        action: Action performed (created, updated, state_change, field_updated, deleted)
        old_value: Previous value (text)
        new_value: New value (text)
        timestamp: When the action occurred
        user_id: Who performed the action (email or system identifier)
    """

    __tablename__ = "audit_logs"
    __table_args__: ClassVar[dict] = {"schema": "finance"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    user_id = Column(String(255), nullable=True)
