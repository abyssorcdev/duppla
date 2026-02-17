"""Application DTOs package.

Contains data transfer objects for API requests and responses.
"""

from app.application.dtos.document_dtos import (
    CreateDocumentRequest,
    DocumentResponse,
    PaginatedDocumentsResponse,
    SearchDocumentsRequest,
    UpdateDocumentRequest,
    UpdateStatusRequest,
)
from app.application.dtos.job_dtos import JobResponse, ProcessBatchRequest

__all__ = [
    "CreateDocumentRequest",
    "DocumentResponse",
    "JobResponse",
    "PaginatedDocumentsResponse",
    "ProcessBatchRequest",
    "SearchDocumentsRequest",
    "UpdateDocumentRequest",
    "UpdateStatusRequest",
]
