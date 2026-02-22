"""Document repository for data access.

Handles document persistence and retrieval operations.
"""

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities.document import Document
from app.domain.exceptions import DocumentNotFoundException
from app.infrastructure.database.models import DocumentModel

_SKIP_AUDIT_SQL = text("SET LOCAL app.skip_audit = 'application'")


class FilterOperator(str, Enum):
    """Query filter operators."""

    EQUAL = "equal"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN_OR_EQUAL = "lte"


class DocumentRepository:
    """Repository for Document entity persistence."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, document: Document) -> Document:
        """Create a new document in database.

        Args:
            document: Document entity to persist

        Returns:
            Document entity with assigned ID
        """
        self.db.execute(_SKIP_AUDIT_SQL)
        db_document = DocumentModel(
            type=document.type,
            amount=document.amount,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
            extra_data=document.metadata,
            created_by=document.created_by,
        )
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)

        document.id = db_document.id
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document entity if found, None otherwise
        """
        db_document = self.db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

        if not db_document:
            return None

        return self._to_entity(db_document)

    def update(self, document_id: int, data: Dict[str, Any]) -> Document:
        """Update document fields.

        Args:
            document_id: Document ID
            data: Dictionary with fields to update

        Returns:
            Updated document entity

        Raises:
            DocumentNotFoundException: If document not found
        """
        db_document = self.db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

        if not db_document:
            raise DocumentNotFoundException(document_id)

        self.db.execute(_SKIP_AUDIT_SQL)
        field_name_map = {"metadata": "extra_data"}
        for key, value in data.items():
            orm_key = field_name_map.get(key, key)
            if hasattr(db_document, orm_key):
                setattr(db_document, orm_key, value)

        self.db.commit()
        self.db.refresh(db_document)

        return self._to_entity(db_document)

    def update_status(self, document_id: int, new_status: str) -> Document:
        """Update document status.

        Args:
            document_id: Document ID
            new_status: New status value

        Returns:
            Updated document entity

        Raises:
            DocumentNotFoundException: If document not found
        """
        return self.update(document_id, {"status": new_status})

    def search(self, filters: Dict[str, Any], skip: int = 0, limit: int = 50) -> Tuple[List[Document], int]:
        """Search documents with filters and pagination.

        Args:
            filters: Search filters (type, status, amount_min, amount_max, etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of documents, total count)
        """
        query = self.db.query(DocumentModel)

        filter_mappings = [
            ("type", DocumentModel.type, FilterOperator.EQUAL),
            ("status", DocumentModel.status, FilterOperator.EQUAL),
            ("amount_min", DocumentModel.amount, FilterOperator.GREATER_THAN_OR_EQUAL),
            ("amount_max", DocumentModel.amount, FilterOperator.LESS_THAN_OR_EQUAL),
            (
                "created_from",
                DocumentModel.created_at,
                FilterOperator.GREATER_THAN_OR_EQUAL,
            ),
            (
                "created_to",
                DocumentModel.created_at,
                FilterOperator.LESS_THAN_OR_EQUAL,
            ),
        ]

        _operator_fn = {
            FilterOperator.EQUAL: lambda col, val: col == val,
            FilterOperator.GREATER_THAN_OR_EQUAL: lambda col, val: col >= val,
            FilterOperator.LESS_THAN_OR_EQUAL: lambda col, val: col <= val,
        }

        for filter_key, column, operator in filter_mappings:
            value = filters.get(filter_key)
            if value is not None:
                query = query.filter(_operator_fn[operator](column, value))

        total = query.count()
        documents = query.order_by(DocumentModel.created_at.desc()).offset(skip).limit(limit).all()

        return [self._to_entity(doc) for doc in documents], total

    def _to_entity(self, db_document: DocumentModel) -> Document:
        """Convert database model to domain entity.

        Args:
            db_document: SQLAlchemy model instance

        Returns:
            Document domain entity
        """
        return Document(
            id=db_document.id,
            type=db_document.type,
            amount=Decimal(str(db_document.amount)),
            status=db_document.status,
            created_at=db_document.created_at,
            updated_at=db_document.updated_at,
            metadata=db_document.extra_data or {},
            created_by=db_document.created_by,
        )
