"""Celery tasks for async batch processing.

Contains task definitions for document batch processing.
"""

import logging
import secrets
import time
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.exc import DatabaseError

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.notifications.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _build_webhook_payload(
    job_id: str,
    status: str,
    document_ids: List[int],
    result: Dict[str, Any],
    error_message: str | None = None,
) -> Dict[str, Any]:
    """Build webhook notification payload.

    Args:
        job_id: Job UUID as string
        status: Final job status
        document_ids: List of processed document IDs
        result: Processing result details
        error_message: Error message if job failed

    Returns:
        Webhook payload dictionary
    """
    payload = {
        "job_id": job_id,
        "status": status,
        "document_ids": document_ids,
        "result": result,
    }

    if error_message:
        payload["error_message"] = error_message

    return payload


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

    Simulates document processing with random delays.
    Updates job status and sends webhook notification on completion.

    Args:
        self: Celery task instance (bound task)
        job_id: Job UUID as string
        document_ids: List of document IDs to process

    Returns:
        Processing result with counts and details
    """
    from app.infrastructure.repositories.job_repository import JobRepository

    db = SessionLocal()
    job_uuid = UUID(job_id)

    try:
        job_repo = JobRepository(db)

        job_repo.update_status(job_uuid, "processing")
        logger.info(f"Started processing batch job {job_id} with {len(document_ids)} documents")

        processed_count = 0
        failed_count = 0
        details = []

        for document_id in document_ids:
            try:
                sleep_time = secrets.randbelow(3) + 1
                time.sleep(sleep_time)

                processed_count += 1
                details.append({"document_id": document_id, "status": "success"})
                logger.debug(f"Processed document {document_id}")

            except Exception as doc_error:
                failed_count += 1
                details.append(
                    {
                        "document_id": document_id,
                        "status": "failed",
                        "error": str(doc_error),
                    }
                )
                logger.warning(f"Failed to process document {document_id}: {doc_error}")

        result = {
            "total": len(document_ids),
            "processed": processed_count,
            "failed": failed_count,
            "details": details,
        }

        job_repo.update_status(
            job_uuid,
            "completed",
            result=result,
        )
        logger.info(f"Completed batch job {job_id}: {processed_count} processed, {failed_count} failed")
        _send_webhook_notification(
            job_id=job_id,
            status="completed",
            document_ids=document_ids,
            result=result,
        )

        return result

    except Exception as error:
        error_message = str(error)
        logger.error(f"Critical failure in batch job {job_id}: {error_message}")

        try:
            job_repo = JobRepository(db)
            job_repo.update_status(
                job_uuid,
                "failed",
                error_message=error_message,
            )

            # Send failure webhook
            _send_webhook_notification(
                job_id=job_id,
                status="failed",
                document_ids=document_ids,
                result={},
                error_message=error_message,
            )
        except Exception as update_error:
            logger.error(f"Failed to update job status: {update_error}")

        raise

    finally:
        db.close()


def _send_webhook_notification(
    job_id: str,
    status: str,
    document_ids: List[int],
    result: Dict[str, Any],
    error_message: str | None = None,
) -> None:
    """Send webhook notification for job completion.

    Args:
        job_id: Job UUID as string
        status: Final job status
        document_ids: List of processed document IDs
        result: Processing result details
        error_message: Error message if job failed
    """
    import asyncio

    from app.core.config import settings
    from app.infrastructure.notifications.clients.webhook_client import WebhookClient

    webhook_url = settings.WEBHOOK_URL
    if not webhook_url:
        logger.debug("No webhook URL configured, skipping notification")
        return

    payload = _build_webhook_payload(
        job_id=job_id,
        status=status,
        document_ids=document_ids,
        result=result,
        error_message=error_message,
    )

    try:
        client = WebhookClient()
        asyncio.run(client.send(webhook_url, payload))
    except Exception as webhook_error:
        logger.error(f"Webhook notification failed for job {job_id}: {webhook_error}")
