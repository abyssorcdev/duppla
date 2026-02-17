"""Domain layer package.

Contains business logic, entities, value objects, and domain rules.
"""

from app.domain.entities import Document, DocumentStatus, Job, JobStatus
from app.domain.exceptions import (
    DocumentNotEditableException,
    DocumentNotFoundException,
    DomainException,
    InvalidAmountException,
    InvalidStateTransitionException,
    JobNotFoundException,
)
from app.domain.state_machine import StateMachine

__all__ = [
    "Document",
    "DocumentNotEditableException",
    "DocumentNotFoundException",
    "DocumentStatus",
    "DomainException",
    "InvalidAmountException",
    "InvalidStateTransitionException",
    "Job",
    "JobNotFoundException",
    "JobStatus",
    "StateMachine",
]
