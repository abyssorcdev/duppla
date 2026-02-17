"""API middleware package.

Contains authentication and error handling middleware.
"""

from app.api.middleware.auth import verify_api_key
from app.api.middleware.error_handler import domain_exception_handler

__all__ = ["domain_exception_handler", "verify_api_key"]
