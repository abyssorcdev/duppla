"""Document API routes.

Endpoints for document CRUD operations.
Role-based access:
  - GET (read): admin, loader, approver
  - POST / PUT (create/edit): admin, loader
  - PATCH status → approved/rejected: admin, approver
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_create_document_service,
    get_get_document_service,
    get_search_documents_service,
    get_update_document_service,
    get_update_status_service,
)
from app.api.middleware.jwt_auth import require_any_active_role, require_approver, require_loader
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
from app.domain.entities.user import User

_active_role_dep = require_any_active_role()
_loader_dep = require_loader()
_approver_dep = require_approver()

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    dependencies=[Depends(_loader_dep)],
)
async def create_document(
    request: CreateDocumentRequest,
    service: CreateDocument = Depends(get_create_document_service),
) -> DocumentResponse:
    """Create a new financial document. Requires admin or loader role."""
    return service.execute(request)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
    dependencies=[Depends(_active_role_dep)],
)
async def get_document(
    document_id: int,
    service: GetDocument = Depends(get_get_document_service),
) -> DocumentResponse:
    """Retrieve a document by its ID."""
    return service.execute(document_id)


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update document fields",
    dependencies=[Depends(_loader_dep)],
)
async def update_document(
    document_id: int,
    request: UpdateDocumentRequest,
    service: UpdateDocument = Depends(get_update_document_service),
) -> DocumentResponse:
    """Update document fields (only in DRAFT status). Requires admin or loader role."""
    return service.execute(document_id, request)


@router.patch(
    "/{document_id}/status",
    response_model=DocumentResponse,
    summary="Update document status",
)
async def update_document_status(
    document_id: int,
    request: UpdateStatusRequest,
    current_user: User = Depends(_approver_dep),
    service: UpdateStatus = Depends(get_update_status_service),
) -> DocumentResponse:
    """Change document status. Requires admin or approver role.

    Valid transitions:
    - DRAFT → PENDING
    - PENDING → APPROVED
    - PENDING → REJECTED
    """
    return service.execute(document_id, request, user_email=current_user.email)


@router.get(
    "",
    response_model=PaginatedDocumentsResponse,
    summary="Search documents with filters",
    dependencies=[Depends(_active_role_dep)],
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
    """Search documents with optional filters and pagination."""
    request = SearchDocumentsRequest(
        type=type,
        status=status,
        amount_min=amount_min,
        amount_max=amount_max,
        page=page,
        page_size=page_size,
    )
    return service.execute(request)
