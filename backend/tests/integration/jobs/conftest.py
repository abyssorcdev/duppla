"""Shared helpers for job integration tests."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from faker import Faker

from app.application.dtos.document_dtos import CreateDocumentRequest
from app.application.services.create_document import CreateDocument

fake = Faker()


def create_documents(db, count=3):
    """Create N draft documents and return their IDs."""
    ids = []
    for _ in range(count):
        request = CreateDocumentRequest(
            type=fake.random_element(["invoice", "receipt", "voucher"]),
            amount=Decimal(str(fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            created_by=fake.bothify("user-####"),
        )
        result = CreateDocument(db=db).execute(request)
        ids.append(result.id)
    return ids


@pytest.fixture()
def mock_celery():
    """Mock the Celery task so it never actually runs."""
    with patch("app.application.services.process_batch.process_documents_batch") as mock_task:
        yield mock_task
