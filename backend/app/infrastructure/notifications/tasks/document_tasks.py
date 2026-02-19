"""Celery tasks for async batch processing.

Contains task definitions for document batch processing.
Processing includes simulated work, business rule evaluation,
status transitions and audit logging — all inline within the task.
"""

import asyncio
import logging
import secrets
import time
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.exc import DatabaseError

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.notifications.dispatcher import NotificationDispatcher
from app.infrastructure.notifications.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


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

    For each document:
    1. Simulates processing work (random delay)
    2. Evaluates business rules via the Document entity
    3. Transitions the document to 'pending' or 'rejected'
    4. Enriches metadata with job_id and rejection reason if applicable
    5. Logs the state change to the audit trail

    Args:
        self: Celery task instance (bound task)
        job_id: Job UUID as string
        document_ids: List of document IDs to process

    Returns:
        Processing result with counts and per-document details
    """
    from app.domain.entities.document.status import DocumentStatus
    from app.domain.state_machine import StateMachine
    from app.infrastructure.repositories.audit_repository import AuditRepository
    from app.infrastructure.repositories.document_repository import DocumentRepository
    from app.infrastructure.repositories.job_repository import JobRepository

    db = SessionLocal()
    job_uuid = UUID(job_id)

    try:
        job_repo = JobRepository(db)
        doc_repo = DocumentRepository(db)
        audit_repo = AuditRepository(db)

        job_repo.update_status(job_uuid, "processing")
        logger.info(f"Started batch job {job_id} — {len(document_ids)} documents")

        processed_count = 0
        failed_count = 0
        details = []

        for document_id in document_ids:
            try:
                time.sleep(secrets.randbelow(9) + 1)

                document = doc_repo.get_by_id(document_id)

                if not document:
                    logger.warning(f"Document {document_id} not found, skipping")
                    details.append({"document_id": document_id, "status": "failed", "error": "not_found"})
                    failed_count += 1
                    continue

                if DocumentStatus.is_final(document.status):
                    logger.info(f"Document {document_id} already in final state ({document.status}), skipping")
                    details.append({"document_id": document_id, "status": "success"})
                    processed_count += 1
                    continue

                old_status = document.status
                new_status, rejection_reason = document.evaluate_for_auto_processing()

                if not StateMachine.validate_transition(old_status, new_status):
                    logger.error(f"Document {document_id}: invalid transition {old_status} → {new_status}, skipping")
                    details.append(
                        {
                            "document_id": document_id,
                            "status": "failed",
                            "error": f"invalid_transition:{old_status}_to_{new_status}",
                        }
                    )
                    failed_count += 1
                    continue

                enriched_metadata = {**document.metadata, "processed_by_job": job_id}
                if rejection_reason:
                    enriched_metadata["rejection_reason"] = rejection_reason

                doc_repo.update(document_id, {"status": new_status, "metadata": enriched_metadata})
                audit_repo.log_action(
                    document_id=document_id,
                    action="state_change",
                    old_value=old_status,
                    new_value=new_status,
                    user_id=f"job:{job_id}",
                )

                logger.info(
                    f"Document {document_id}: {old_status} → {new_status}"
                    + (f" (reason: {rejection_reason})" if rejection_reason else "")
                )
                details.append({"document_id": document_id, "status": "success"})
                processed_count += 1

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
        logger.info(f"Batch job {job_id} completed: {processed_count} processed, {failed_count} failed")

        _notify_completion(job_id=job_id, status="completed", document_ids=document_ids, result=result)

        return result

    except Exception as error:
        error_message = str(error)
        logger.error(f"Critical failure in batch job {job_id}: {error_message}")

        try:
            job_repo = JobRepository(db)
            job_repo.update_status(job_uuid, "failed", error_message=error_message)
            _notify_completion(
                job_id=job_id,
                status="failed",
                document_ids=document_ids,
                result={
                    "total": len(document_ids),
                    "processed": 0,
                    "failed": len(document_ids),
                    "details": [
                        {"document_id": doc_id, "status": "failed", "error": error_message} for doc_id in document_ids
                    ],
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
    """Dispatch job completion notifications to all configured channels.

    Args:
        job_id: Job UUID as string
        status: Final job status
        document_ids: All document IDs in the batch
        result: Processing result details
        error_message: Critical error message if job failed entirely
    """
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
