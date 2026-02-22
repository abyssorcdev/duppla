"""Service dependencies for dependency injection.

Provides application services with database session injection.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_database
from app.application.services import (
    CreateDocument,
    GetDocument,
    GetJobStatus,
    ListJobs,
    ProcessBatch,
    SearchDocuments,
    UpdateDocument,
    UpdateStatus,
)


def get_create_document_service(
    db: Session = Depends(get_database),
) -> CreateDocument:
    """Get CreateDocument service instance."""
    return CreateDocument(db)


def get_get_document_service(db: Session = Depends(get_database)) -> GetDocument:
    """Get GetDocument service instance."""
    return GetDocument(db)


def get_update_document_service(
    db: Session = Depends(get_database),
) -> UpdateDocument:
    """Get UpdateDocument service instance."""
    return UpdateDocument(db)


def get_update_status_service(db: Session = Depends(get_database)) -> UpdateStatus:
    """Get UpdateStatus service instance."""
    return UpdateStatus(db)


def get_search_documents_service(
    db: Session = Depends(get_database),
) -> SearchDocuments:
    """Get SearchDocuments service instance."""
    return SearchDocuments(db)


def get_process_batch_service(db: Session = Depends(get_database)) -> ProcessBatch:
    """Get ProcessBatch service instance."""
    return ProcessBatch(db)


def get_get_job_status_service(
    db: Session = Depends(get_database),
) -> GetJobStatus:
    """Get GetJobStatus service instance."""
    return GetJobStatus(db)


def get_list_jobs_service(db: Session = Depends(get_database)) -> ListJobs:
    """Get ListJobs service instance."""
    return ListJobs(db)
