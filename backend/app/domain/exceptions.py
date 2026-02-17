"""Domain layer exceptions.

Custom exceptions for business logic and domain rules.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidStateTransitionException(DomainException):
    """Raised when attempting an invalid state transition."""

    def __init__(self, current_state: str, new_state: str) -> None:
        self.current_state = current_state
        self.new_state = new_state
        message = f"Cannot transition from '{current_state}' to '{new_state}'. Invalid state transition."
        super().__init__(message)


class DocumentNotFoundException(DomainException):
    """Raised when a document is not found."""

    def __init__(self, document_id: int) -> None:
        self.document_id = document_id
        message = f"Document with id {document_id} not found"
        super().__init__(message)


class JobNotFoundException(DomainException):
    """Raised when a job is not found."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        message = f"Job with id {job_id} not found"
        super().__init__(message)


class InvalidAmountException(DomainException):
    """Raised when amount is invalid."""

    def __init__(self, amount: float) -> None:
        self.amount = amount
        message = f"Invalid amount: {amount}. Amount must be greater than 0"
        super().__init__(message)


class DocumentNotEditableException(DomainException):
    """Raised when trying to edit a document that is not in DRAFT state."""

    def __init__(self, document_id: int, current_state: str) -> None:
        self.document_id = document_id
        self.current_state = current_state
        message = (
            f"Cannot edit document {document_id}. "
            f"Only documents in DRAFT state can be edited. "
            f"Current state: {current_state}"
        )
        super().__init__(message)
