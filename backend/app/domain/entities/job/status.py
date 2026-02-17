"""Job status value object.

Defines valid statuses for batch processing jobs.
"""

from enum import Enum


class JobStatus(str, Enum):
    """Valid statuses for a batch processing job.

    Workflow:
        PENDING → PROCESSING → COMPLETED/FAILED

    - PENDING: Job created, waiting for worker
    - PROCESSING: Worker is currently processing
    - COMPLETED: Processing finished successfully
    - FAILED: Processing failed after retries
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
