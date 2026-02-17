"""Error handler middleware for consistent API error responses.

Handles domain exceptions and converts them to appropriate HTTP responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    DocumentNotEditableException,
    DocumentNotFoundException,
    DomainException,
    InvalidAmountException,
    InvalidStateTransitionException,
    JobNotFoundException,
)


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle domain exceptions and return appropriate HTTP responses.

    Args:
        request: FastAPI request
        exc: Domain exception

    Returns:
        JSON response with error details
    """
    status_code_map = {
        DocumentNotFoundException: status.HTTP_404_NOT_FOUND,
        JobNotFoundException: status.HTTP_404_NOT_FOUND,
        InvalidStateTransitionException: status.HTTP_400_BAD_REQUEST,
        InvalidAmountException: status.HTTP_400_BAD_REQUEST,
        DocumentNotEditableException: status.HTTP_400_BAD_REQUEST,
        DomainException: status.HTTP_400_BAD_REQUEST,
    }

    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
        },
    )
