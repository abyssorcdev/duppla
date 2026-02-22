"""API routes package.

Contains all API endpoint routers.
"""

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.batch import router as batch_router
from app.api.routes.documents import router as documents_router
from app.api.routes.jobs import router as jobs_router

__all__ = ["admin_router", "auth_router", "batch_router", "documents_router", "jobs_router"]
