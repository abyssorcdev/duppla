"""Document SQLAlchemy model.

Maps Document domain entity to documents database table.
"""

from typing import Any, Dict

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.infrastructure.database.models.base import Base


class DocumentModel(Base):
    """SQLAlchemy model for documents table.

    Attributes:
        id: Primary key
        type: Document type (invoice, receipt, voucher)
        amount: Document amount (must be > 0)
        status: Current status (draft, pending, approved, rejected)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional flexible data (JSON)
        created_by: User who created the document
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    amount = Column(Numeric(12, 2), CheckConstraint("amount > 0"), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    metadata = Column(JSONB, nullable=False, default={})
    created_by = Column(String(100), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary representation of the document
        """
        return {
            "id": self.id,
            "type": self.type,
            "amount": float(self.amount),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "created_by": self.created_by,
        }
