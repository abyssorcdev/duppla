"""Document API routes.

Endpoints for document CRUD operations.
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_create_document_service,
    get_get_document_service,
    get_search_documents_service,
    get_update_document_service,
    get_update_status_service,
)
from app.api.middleware.auth import verify_api_key
from app.application.dtos.document_dtos import (
    CreateDocumentRequest,
    DocumentResponse,
    PaginatedDocumentsResponse,
    SearchDocumentsRequest,
    UpdateDocumentRequest,
    UpdateStatusRequest,
)
from app.application.services import (
    CreateDocument,
    GetDocument,
    SearchDocuments,
    UpdateDocument,
    UpdateStatus,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
)
async def create_document(
    request: CreateDocumentRequest,
    service: CreateDocument = Depends(get_create_document_service),
) -> DocumentResponse:
    """Create a new financial document.

    - **type**: Document type (invoice, receipt, voucher, etc.)
    - **amount**: Document amount (must be > 0)
    - **metadata**: Additional flexible data (optional)
    - **created_by**: User who created the document (optional)

    Returns the created document with ID and initial status (draft).
    """
    return service.execute(request)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
)
async def get_document(
    document_id: int,
    service: GetDocument = Depends(get_get_document_service),
) -> DocumentResponse:
    """Retrieve a document by its ID.

    - **document_id**: Document ID to retrieve

    Returns the document details or 404 if not found.
    """
    return service.execute(document_id)


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update document fields",
)
async def update_document(
    document_id: int,
    request: UpdateDocumentRequest,
    service: UpdateDocument = Depends(get_update_document_service),
) -> DocumentResponse:
    """Update document fields (only in DRAFT status).

    - **document_id**: Document ID to update
    - **type**: New document type (optional)
    - **amount**: New amount (optional, must be > 0)
    - **metadata**: New metadata (optional)

    Returns the updated document or 400 if not editable.
    """
    return service.execute(document_id, request)


@router.patch(
    "/{document_id}/status",
    response_model=DocumentResponse,
    summary="Update document status",
)
async def update_document_status(
    document_id: int,
    request: UpdateStatusRequest,
    service: UpdateStatus = Depends(get_update_status_service),
) -> DocumentResponse:
    """Change document status with validation.

    Valid transitions:
    - DRAFT → PENDING
    - PENDING → APPROVED
    - PENDING → REJECTED

    - **document_id**: Document ID to update
    - **new_status**: Target status (pending, approved, rejected)

    Returns the updated document or 400 if transition is invalid.
    Logs the change in audit logs.
    """
    return service.execute(document_id, request)


@router.get(
    "",
    response_model=PaginatedDocumentsResponse,
    summary="Search documents with filters",
)
async def search_documents(
    type: str | None = None,
    status: str | None = None,
    amount_min: float | None = None,
    amount_max: float | None = None,
    page: int = 1,
    page_size: int = 50,
    service: SearchDocuments = Depends(get_search_documents_service),
) -> PaginatedDocumentsResponse:
    """Search documents with optional filters and pagination.

    - **type**: Filter by document type (optional)
    - **status**: Filter by status (optional)
    - **amount_min**: Minimum amount filter (optional)
    - **amount_max**: Maximum amount filter (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)

    Returns paginated list of documents matching the filters.
    """
    request = SearchDocumentsRequest(
        type=type,
        status=status,
        amount_min=amount_min,
        amount_max=amount_max,
        page=page,
        page_size=page_size,
    )
    return service.execute(request)
