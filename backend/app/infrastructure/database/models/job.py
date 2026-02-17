"""Job SQLAlchemy model.

Maps Job domain entity to jobs database table.
"""

from typing import Any, Dict

from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.sql import func

from app.infrastructure.database.models.base import Base


class JobModel(Base):
    """SQLAlchemy model for jobs table.

    Attributes:
        id: UUID primary key
        document_ids: Array of document IDs to process
        status: Current status (pending, processing, completed, failed)
        created_at: Creation timestamp
        completed_at: Completion timestamp
        error_message: Error message if job failed
        result: Processing result details (JSON)
    """

    __tablename__ = "jobs"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    document_ids = Column(ARRAY(Integer), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result = Column(JSONB, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary representation of the job
        """
        return {
            "id": self.id,
            "document_ids": self.document_ids,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "result": self.result,
        }
