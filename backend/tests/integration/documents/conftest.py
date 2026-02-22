"""Shared helpers for document integration tests."""

from decimal import Decimal

from faker import Faker

from app.application.dtos.document_dtos import CreateDocumentRequest
from app.application.services.create_document import CreateDocument

fake = Faker()


def create_draft(db, **overrides):
    """Create a DRAFT document and return the response."""
    defaults = dict(
        type=fake.random_element(["invoice", "receipt", "voucher"]),
        amount=Decimal(str(fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
        created_by=fake.bothify("user-####"),
    )
    defaults.update(overrides)
    request = CreateDocumentRequest(**defaults)
    return CreateDocument(db=db).execute(request)
