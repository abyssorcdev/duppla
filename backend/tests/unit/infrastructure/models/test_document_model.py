"""Tests for app.infrastructure.database.models.document.DocumentModel.to_dict."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from tests.common import BaseTestCase


class TestDocumentModelToDict(BaseTestCase):
    """Tests for DocumentModel.to_dict()."""

    def _make_model(self) -> MagicMock:
        model = MagicMock()
        model.id = self.fake.random_int(min=1, max=999)
        model.type = self.fake.random_element(["invoice", "receipt", "voucher"])
        model.amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))
        model.status = "draft"
        model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()
        model.extra_data = {"client": self.fake.company()}
        model.created_by = self.fake.email()
        return model

    def test_to_dict_success_returns_all_keys(self) -> None:
        from app.infrastructure.database.models.document import DocumentModel

        model = self._make_model()
        result = DocumentModel.to_dict(model)
        expected_keys = {"id", "type", "amount", "status", "created_at", "updated_at", "metadata", "created_by"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_to_dict_success_metadata_maps_from_extra_data(self) -> None:
        from app.infrastructure.database.models.document import DocumentModel

        model = self._make_model()
        result = DocumentModel.to_dict(model)
        self.assertEqual(result["metadata"], model.extra_data)

    def test_to_dict_success_amount_is_float(self) -> None:
        from app.infrastructure.database.models.document import DocumentModel

        model = self._make_model()
        result = DocumentModel.to_dict(model)
        self.assertIsInstance(result["amount"], float)
