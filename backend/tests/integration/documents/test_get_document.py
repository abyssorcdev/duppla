"""Integration tests for GetDocument service (GET)."""

from decimal import Decimal

import pytest

from app.application.services.get_document import GetDocument
from app.domain.exceptions import DocumentNotFoundException

from .conftest import create_draft, fake


class TestGetDocument:
    """Verify GetDocument reads actual rows from the database."""

    def test_get_returns_persisted_data(self, db):
        """
        When: A document is created
        Then: GetDocument should return it by ID with correct data
        """
        doc_type = fake.random_element(["invoice", "receipt", "voucher"])
        amount = Decimal(str(fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        result = create_draft(db, type=doc_type, amount=amount)

        fetched = GetDocument(db=db).execute(result.id)

        assert fetched.id == result.id
        assert fetched.type == doc_type
        assert fetched.amount == amount
        assert fetched.status == "draft"

    def test_get_not_found(self, db):
        """
        When: Document ID does not exist
        Then: Should raise DocumentNotFoundException
        """
        not_found_id = fake.random_int(min=900_000, max=999_999)
        with pytest.raises(DocumentNotFoundException):
            GetDocument(db=db).execute(not_found_id)
