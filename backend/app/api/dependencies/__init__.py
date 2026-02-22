"""API dependencies package.

Provides dependency injection functions for FastAPI.
"""

from app.api.dependencies.database import get_database
from app.api.dependencies.services import (
    get_create_document_service,
    get_get_document_service,
    get_get_job_status_service,
    get_list_jobs_service,
    get_process_batch_service,
    get_search_documents_service,
    get_update_document_service,
    get_update_status_service,
)

__all__ = [
    "get_create_document_service",
    "get_database",
    "get_get_document_service",
    "get_get_job_status_service",
    "get_list_jobs_service",
    "get_process_batch_service",
    "get_search_documents_service",
    "get_update_document_service",
    "get_update_status_service",
]
