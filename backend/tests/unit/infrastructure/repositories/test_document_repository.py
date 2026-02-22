"""Tests for app.infrastructure.repositories.document_repository.DocumentRepository – coverage gaps."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.domain.exceptions import DocumentNotFoundException


class DocumentRepositoryTestCase(BaseTestCase):
    """Base class for DocumentRepository tests."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        with patch("app.infrastructure.repositories.document_repository._SKIP_AUDIT_SQL"):
            from app.infrastructure.repositories.document_repository import DocumentRepository

            self.repo = DocumentRepository(self.mock_db)

    def _make_db_model(self, **overrides):
        model = MagicMock()
        model.id = overrides.get("id", self.fake.random_int(min=1))
        model.type = overrides.get("type", "invoice")
        model.amount = overrides.get("amount", Decimal("100.00"))
        model.status = overrides.get("status", "draft")
        model.created_at = self.test_timestamp
        model.updated_at = self.test_timestamp
        model.extra_data = overrides.get("extra_data", {})
        model.created_by = overrides.get("created_by", self.fake.email())
        return model


class TestCreate(DocumentRepositoryTestCase):
    """Tests for create()."""

    def test_create_success(self) -> None:
        doc = self.make_document()
        db_model = self._make_db_model(id=42)
        self.mock_db.refresh.side_effect = lambda m: setattr(m, "id", 42)

        self.repo.create(doc)

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()


class TestGetById(DocumentRepositoryTestCase):
    """Tests for get_by_id()."""

    def test_get_by_id_success_found(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.get_by_id(1)
        self.assertIsNotNone(result)
        self.assertEqual(result.type, db_model.type)

    def test_get_by_id_success_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.repo.get_by_id(999)
        self.assertIsNone(result)


class TestUpdate(DocumentRepositoryTestCase):
    """Tests for update()."""

    def test_update_success(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.update(1, {"status": "pending"})
        self.mock_db.commit.assert_called()

    def test_update_success_metadata_maps_to_extra_data(self) -> None:
        db_model = self._make_db_model()
        db_model.extra_data = {}
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        new_meta = {"client": self.fake.company()}
        self.repo.update(1, {"metadata": new_meta})
        self.assertEqual(db_model.extra_data, new_meta)

    def test_update_success_skips_unknown_field(self) -> None:
        db_model = self._make_db_model()
        del db_model.nonexistent_field
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        self.repo.update(1, {"status": "pending", "nonexistent_field": "val"})
        self.mock_db.commit.assert_called()

    def test_update_error_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(DocumentNotFoundException):
            self.repo.update(999, {"status": "pending"})


class TestUpdateStatus(DocumentRepositoryTestCase):
    """Tests for update_status()."""

    def test_update_status_success(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model

        result = self.repo.update_status(1, "pending")
        self.mock_db.commit.assert_called()


class TestSearch(DocumentRepositoryTestCase):
    """Tests for search()."""

    def test_search_success_no_filters(self) -> None:
        db_models = [self._make_db_model(), self._make_db_model()]
        mock_query = MagicMock()
        mock_query.count.return_value = 2
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = db_models
        self.mock_db.query.return_value = mock_query

        docs, total = self.repo.search({})
        self.assertEqual(total, 2)
        self.assertEqual(len(docs), 2)

    def test_search_success_type_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 1
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self._make_db_model()]
        self.mock_db.query.return_value = mock_query

        docs, total = self.repo.search({"type": "invoice"})
        self.assertEqual(total, 1)

    def test_search_success_amount_min_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 0
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query

        docs, total = self.repo.search({"amount_min": Decimal("500")})
        self.assertEqual(total, 0)

    def test_search_success_amount_max_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 0
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query

        docs, total = self.repo.search({"amount_max": Decimal("1000")})
        self.assertEqual(total, 0)

    def test_search_success_status_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 0
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query

        docs, total = self.repo.search({"status": "draft"})
        self.assertEqual(total, 0)

    def test_search_success_date_filters(self) -> None:
        mock_query = MagicMock()
        mock_f1 = MagicMock()
        mock_f2 = MagicMock()
        mock_query.filter.return_value = mock_f1
        mock_f1.filter.return_value = mock_f2
        mock_f2.count.return_value = 0
        mock_f2.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query

        from datetime import datetime

        docs, total = self.repo.search({
            "created_from": datetime(2024, 1, 1),
            "created_to": datetime(2024, 12, 31),
        })
        self.assertEqual(total, 0)
