"""API middleware package.

Contains authentication and error handling middleware.
"""

from app.api.middleware.auth import verify_api_key
from app.api.middleware.error_handler import domain_exception_handler, validation_exception_handler
from app.api.middleware.jwt_auth import (
    get_current_user,
    require_admin,
    require_any_active_role,
    require_approver,
    require_loader,
    require_roles,
)

__all__ = [
    "domain_exception_handler",
    "get_current_user",
    "require_admin",
    "require_any_active_role",
    "require_approver",
    "require_loader",
    "require_roles",
    "validation_exception_handler",
    "verify_api_key",
]
