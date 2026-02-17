"""API routes package.

Contains all API endpoint routers.
"""

from app.api.routes.batch import router as batch_router
from app.api.routes.documents import router as documents_router

__all__ = ["batch_router", "documents_router"]
