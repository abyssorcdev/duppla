"""Error handler middleware for consistent API error responses.

Handles domain exceptions and converts them to appropriate HTTP responses.
"""

from typing import Any, Dict, List

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
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


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors with user-friendly messages.

    Transforms the default verbose 422 error into a clean list of field errors.

    Args:
        request: FastAPI request
        exc: Pydantic validation error

    Returns:
        JSON response with structured field errors

    Example response:
        {
            "error": "ValidationError",
            "message": "Request validation failed",
            "fields": [
                {"field": "amount", "message": "Amount cannot exceed 999999999.99"},
                {"field": "type", "message": "Input should be 'invoice', 'receipt'..."}
            ]
        }
    """
    fields: List[Dict[str, Any]] = []

    for error in exc.errors():
        location = error.get("loc", [])
        field = ".".join(str(part) for part in location if part != "body")
        message = error.get("msg", "Invalid value")
        message = message.removeprefix("Value error, ")

        fields.append({"field": field or "unknown", "message": message})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "fields": fields,
        },
    )
