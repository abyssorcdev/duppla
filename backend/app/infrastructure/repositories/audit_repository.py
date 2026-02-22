"""Audit log repository.

Generic audit trail for all tables (documents, jobs, users).
Uses (table_name, record_id) to avoid coupling to a specific table.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.infrastructure.database.models import AuditLogModel


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Write ─────────────────────────────────────────────────────────────────

    def log(
        self,
        table_name: str,
        record_id: str,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Append a generic audit entry.

        Args:
            table_name: Affected table (e.g. 'documents', 'jobs', 'users')
            record_id:  String-serialized PK of the affected row
            action:     'created' | 'updated' | 'state_change' | 'field_updated' | 'deleted'
            old_value:  Previous value (optional)
            new_value:  New value (optional)
            user_id:    Who triggered the action
        """
        entry = AuditLogModel(
            table_name=table_name,
            record_id=str(record_id),
            action=action,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.utcnow(),
            user_id=user_id,
        )
        self.db.add(entry)
        self.db.commit()

    # ── Convenience shorthands ────────────────────────────────────────────────

    def log_created(self, table_name: str, record_id: str, summary: str, user_id: Optional[str] = None) -> None:
        self.log(table_name, record_id, "created", new_value=summary, user_id=user_id)

    def log_state_change(
        self, table_name: str, record_id: str, old_state: str, new_state: str, user_id: Optional[str] = None
    ) -> None:
        self.log(table_name, record_id, "state_change", old_value=old_state, new_value=new_state, user_id=user_id)

    def log_field_updated(
        self, table_name: str, record_id: str, old_value: str, new_value: str, user_id: Optional[str] = None
    ) -> None:
        self.log(table_name, record_id, "field_updated", old_value=old_value, new_value=new_value, user_id=user_id)

    # ── Read ──────────────────────────────────────────────────────────────────

    def list_recent(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> Tuple[List[AuditLogModel], int]:
        """Return recent audit entries with optional filters."""
        query = self.db.query(AuditLogModel)
        if action:
            query = query.filter(AuditLogModel.action == action)
        if table_name:
            query = query.filter(AuditLogModel.table_name == table_name)
        total = query.count()
        entries = query.order_by(AuditLogModel.timestamp.desc()).offset(skip).limit(limit).all()
        return entries, total
