"""Document entity package.

Contains the Document entity and related value objects.
"""

from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus

__all__ = ["Document", "DocumentStatus"]
