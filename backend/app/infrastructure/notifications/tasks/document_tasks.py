"""Celery tasks for async batch processing.

Each document status is handled by a dedicated function registered in
STATUS_HANDLERS. Adding support for a new status only requires writing
a new handler and adding one entry to the map — the task loop stays unchanged.
"""

import asyncio
import logging
import secrets
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple
from uuid import UUID

if TYPE_CHECKING:
    from app.domain.entities.document.document import Document
    from app.infrastructure.repositories.audit_repository import AuditRepository
    from app.infrastructure.repositories.document_repository import DocumentRepository

from sqlalchemy.exc import DatabaseError

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.notifications.dispatcher import NotificationDispatcher
from app.infrastructure.notifications.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# (document, doc_repo, audit_repo, job_id) → (detail_dict, succeeded: bool)
_Handler = Callable[..., Tuple[Dict[str, Any], bool]]


def _handle_rejected(
    document: "Document", doc_repo: "DocumentRepository", audit_repo: "AuditRepository", job_id: str
) -> Tuple[Dict, bool]:
    """Reset a rejected document to draft so it can be corrected and re-submitted."""
    from app.domain.entities.document.status import DocumentStatus

    doc_repo.update(document.id, {"status": DocumentStatus.DRAFT.value})
    audit_repo.log_state_change(
        table_name="documents",
        record_id=str(document.id),
        old_state=DocumentStatus.REJECTED.value,
        new_state=DocumentStatus.DRAFT.value,
        user_id=f"job:{job_id}",
    )
    logger.info(f"Document {document.id}: rejected → draft (reset for re-processing)")
    return {"document_id": document.id, "status": "success", "action": "reset_to_draft"}, True


def _handle_draft(
    document: "Document", doc_repo: "DocumentRepository", audit_repo: "AuditRepository", job_id: str
) -> Tuple[Dict, bool]:
    """Evaluate business rules and transition a draft document to pending or rejected."""
    from app.domain.state_machine import StateMachine

    old_status = document.status
    new_status, rejection_reason = document.evaluate_for_auto_processing()

    if not StateMachine.validate_transition(old_status, new_status):
        logger.error(f"Document {document.id}: invalid transition {old_status} → {new_status}")
        return {
            "document_id": document.id,
            "status": "failed",
            "error": f"invalid_transition:{old_status}_to_{new_status}",
        }, False

    enriched_metadata = {**document.metadata, "processed_by_job": job_id}
    if rejection_reason:
        enriched_metadata["rejection_reason"] = rejection_reason

    doc_repo.update(document.id, {"status": new_status, "metadata": enriched_metadata})
    audit_repo.log_state_change(
        table_name="documents",
        record_id=str(document.id),
        old_state=old_status,
        new_state=new_status,
        user_id=f"job:{job_id}",
    )
    logger.info(
        f"Document {document.id}: {old_status} → {new_status}"
        + (f" (reason: {rejection_reason})" if rejection_reason else "")
    )
    return {"document_id": document.id, "status": "success"}, True


def _handle_final(
    document: "Document", doc_repo: "DocumentRepository", audit_repo: "AuditRepository", job_id: str
) -> Tuple[Dict, bool]:
    """Skip a document that is already in a truly final state (approved)."""
    logger.info(f"Document {document.id} already in final state ({document.status}), skipping")
    return {"document_id": document.id, "status": "success", "action": "skipped"}, True


def _handle_unknown(
    document: "Document", doc_repo: "DocumentRepository", audit_repo: "AuditRepository", job_id: str
) -> Tuple[Dict, bool]:
    """Fail gracefully for any unrecognised status."""
    logger.warning(f"Document {document.id}: unhandled status '{document.status}'")
    return {"document_id": document.id, "status": "failed", "error": f"unhandled_status:{document.status}"}, False


def _build_handlers() -> Dict[str, _Handler]:
    from app.domain.entities.document.status import DocumentStatus

    return {
        DocumentStatus.REJECTED.value: _handle_rejected,
        DocumentStatus.DRAFT.value: _handle_draft,
        DocumentStatus.APPROVED.value: _handle_final,
        DocumentStatus.PENDING.value: _handle_final,
    }


@celery_app.task(
    name="process_documents_batch",
    autoretry_for=(DatabaseError, ConnectionError),
    max_retries=3,
    retry_backoff=True,
    bind=True,
)
def process_documents_batch(
    self,  # noqa: ANN001
    job_id: str,
    document_ids: List[int],
) -> Dict[str, Any]:
    """Process a batch of documents asynchronously.

    For each document the appropriate handler is looked up from STATUS_HANDLERS.
    Adding behaviour for a new status only requires a new handler + one map entry.

    Args:
        self: Celery task instance (bound task)
        job_id: Job UUID as string
        document_ids: List of document IDs to process

    Returns:
        Processing result with counts and per-document details
    """
    from app.infrastructure.repositories.audit_repository import AuditRepository
    from app.infrastructure.repositories.document_repository import DocumentRepository
    from app.infrastructure.repositories.job_repository import JobRepository

    db = SessionLocal()
    job_uuid = UUID(job_id)

    try:
        job_repo = JobRepository(db)
        doc_repo = DocumentRepository(db)
        audit_repo = AuditRepository(db)
        handlers = _build_handlers()

        job_repo.update_status(job_uuid, "processing")
        audit_repo.log_state_change(
            table_name="jobs",
            record_id=job_id,
            old_state="pending",
            new_state="processing",
            user_id="celery-worker",
        )
        logger.info(f"Started batch job {job_id} — {len(document_ids)} documents")

        processed_count = 0
        failed_count = 0
        details: List[Dict[str, Any]] = []

        for document_id in document_ids:
            try:
                time.sleep(secrets.randbelow(9) + 1)

                document = doc_repo.get_by_id(document_id)
                if not document:
                    logger.warning(f"Document {document_id} not found, skipping")
                    details.append({"document_id": document_id, "status": "failed", "error": "not_found"})
                    failed_count += 1
                    continue

                handler = handlers.get(document.status, _handle_unknown)
                detail, succeeded = handler(document, doc_repo, audit_repo, job_id)

                details.append(detail)
                if succeeded:
                    processed_count += 1
                else:
                    failed_count += 1

            except Exception as doc_error:
                failed_count += 1
                details.append({"document_id": document_id, "status": "failed", "error": str(doc_error)})
                logger.warning(f"Failed to process document {document_id}: {doc_error}")

        result = {
            "total": len(document_ids),
            "processed": processed_count,
            "failed": failed_count,
            "details": details,
        }

        job_repo.update_status(job_uuid, "completed", result=result)
        audit_repo.log_state_change(
            table_name="jobs",
            record_id=job_id,
            old_state="processing",
            new_state="completed",
            user_id="celery-worker",
        )
        logger.info(f"Batch job {job_id} completed: {processed_count} processed, {failed_count} failed")
        _notify_completion(job_id=job_id, status="completed", document_ids=document_ids, result=result)

        return result

    except Exception as error:
        error_message = str(error)
        logger.error(f"Critical failure in batch job {job_id}: {error_message}")
        try:
            job_repo.update_status(job_uuid, "failed", error_message=error_message)
            audit_repo.log_state_change(
                table_name="jobs",
                record_id=job_id,
                old_state="processing",
                new_state="failed",
                user_id="celery-worker",
            )
            _notify_completion(
                job_id=job_id,
                status="failed",
                document_ids=document_ids,
                result={
                    "total": len(document_ids),
                    "processed": 0,
                    "failed": len(document_ids),
                    "details": [{"document_id": d, "status": "failed", "error": error_message} for d in document_ids],
                },
                error_message=error_message,
            )
        except Exception as update_error:
            logger.error(f"Failed to update job status after critical failure: {update_error}")
        raise

    finally:
        db.close()


def _notify_completion(
    job_id: str,
    status: str,
    document_ids: List[int],
    result: Dict[str, Any],
    error_message: str | None = None,
) -> None:
    """Dispatch job completion notifications to all configured channels."""
    payload: Dict[str, Any] = {
        "job_id": job_id,
        "status": status,
        "document_ids": document_ids,
        "result": result,
    }
    if error_message:
        payload["error_message"] = error_message

    try:
        dispatch_result = asyncio.run(NotificationDispatcher.from_config().dispatch(payload))
        if not dispatch_result.all_succeeded:
            logger.warning(
                f"Job {job_id} — notification partial failure: "
                f"ok={dispatch_result.succeeded}, failed={dispatch_result.failed}"
            )
    except Exception as e:
        logger.error(f"Notification dispatch failed for job {job_id}: {e}")
