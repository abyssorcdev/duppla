"""Audit log SQLAlchemy model.

Maps audit log to audit_logs database table.
"""

from typing import Any, ClassVar, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.infrastructure.database.models.base import Base


class AuditLogModel(Base):
    """SQLAlchemy model for audit_logs table.

    Tracks document lifecycle events (created, updated, deleted, state_change, field_updated).

    Attributes:
        id: Primary key
        document_id: Foreign key to documents table
        action: Action performed (created, updated, deleted, state_change, field_updated)
        old_value: Previous value (optional, can store any field value as text)
        new_value: New value (optional, can store any field value as text)
        timestamp: Action timestamp
        user_id: User who performed the action
    """

    __tablename__ = "audit_logs"
    __table_args__: ClassVar[dict] = {"schema": "finance"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("finance.documents.id"), nullable=False)
    action = Column(String(50), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    user_id = Column(String(100), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary representation of the audit log
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
        }
