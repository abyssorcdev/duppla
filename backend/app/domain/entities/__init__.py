"""Domain entities package.

Contains core business entities.
"""

from app.domain.entities.document import Document, DocumentStatus
from app.domain.entities.job import Job, JobStatus

__all__ = ["Document", "DocumentStatus", "Job", "JobStatus"]
