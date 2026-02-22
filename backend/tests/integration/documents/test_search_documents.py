"""Integration tests for SearchDocuments service (GET)."""

from decimal import Decimal

from app.application.dtos.document_dtos import SearchDocumentsRequest
from app.application.services.search_documents import SearchDocuments

from .conftest import create_draft, fake


class TestSearchDocuments:
    """Verify SearchDocuments queries real data."""

    def test_search_by_type(self, db):
        """
        When: Multiple documents exist with different types
        Then: Search filtered by type returns only matching ones
        """
        amount1 = Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))
        amount2 = Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))
        amount3 = Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))

        create_draft(db, type="invoice", amount=amount1)
        create_draft(db, type="receipt", amount=amount2)
        create_draft(db, type="invoice", amount=amount3)

        result = SearchDocuments(db=db).execute(
            SearchDocumentsRequest(type="invoice")
        )

        assert result.total >= 2
        for item in result.items:
            assert item.type == "invoice"

    def test_search_empty_result(self, db):
        """
        When: No documents match the filter
        Then: Should return empty items with total=0
        """
        nonexistent_type = fake.bothify("type-????-####")
        result = SearchDocuments(db=db).execute(
            SearchDocumentsRequest(type=nonexistent_type)
        )

        assert result.total == 0
        assert len(result.items) == 0

    def test_search_pagination(self, db):
        """
        When: More documents exist than page_size
        Then: Should return paginated results with correct totals
        """
        for _ in range(5):
            create_draft(db, type="voucher")

        result = SearchDocuments(db=db).execute(
            SearchDocumentsRequest(type="voucher", page=1, page_size=2)
        )

        assert len(result.items) == 2
        assert result.total >= 5
        assert result.page == 1
