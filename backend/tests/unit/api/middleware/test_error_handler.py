"""Tests for app.api.middleware.error_handler."""

import asyncio
from unittest.mock import MagicMock

from tests.common import BaseTestCase

from app.api.middleware.error_handler import (
    domain_exception_handler,
    validation_exception_handler,
)
from app.domain.exceptions import (
    DocumentNotEditableException,
    DocumentNotFoundException,
    DomainException,
    InvalidAmountException,
    InvalidStateTransitionException,
    JobNotFoundException,
)


class TestDomainExceptionHandler(BaseTestCase):
    """Tests for domain_exception_handler()."""

    def _run(self, exc):
        request = MagicMock()
        return asyncio.run(domain_exception_handler(request, exc))

    def test_document_not_found_returns_404(self) -> None:
        resp = self._run(DocumentNotFoundException(self.fake.random_int()))
        self.assertEqual(resp.status_code, 404)

    def test_job_not_found_returns_404(self) -> None:
        resp = self._run(JobNotFoundException(str(self.fake.uuid4())))
        self.assertEqual(resp.status_code, 404)

    def test_invalid_state_transition_returns_400(self) -> None:
        resp = self._run(InvalidStateTransitionException("draft", "approved"))
        self.assertEqual(resp.status_code, 400)

    def test_invalid_amount_returns_400(self) -> None:
        resp = self._run(InvalidAmountException(-1))
        self.assertEqual(resp.status_code, 400)

    def test_document_not_editable_returns_400(self) -> None:
        resp = self._run(DocumentNotEditableException(1, "pending"))
        self.assertEqual(resp.status_code, 400)

    def test_generic_domain_exception_returns_400(self) -> None:
        resp = self._run(DomainException("generic error"))
        self.assertEqual(resp.status_code, 400)

    def test_response_contains_error_key(self) -> None:
        import json

        resp = self._run(DocumentNotFoundException(1))
        body = json.loads(resp.body)
        self.assertIn("error", body)
        self.assertIn("message", body)


class TestValidationExceptionHandler(BaseTestCase):
    """Tests for validation_exception_handler()."""

    def test_validation_error_returns_422(self) -> None:
        from fastapi.exceptions import RequestValidationError

        exc = RequestValidationError(
            errors=[
                {"loc": ("body", "amount"), "msg": "Value error, Amount cannot exceed 999999999.99", "type": "value_error"}
            ]
        )
        request = MagicMock()
        resp = asyncio.run(validation_exception_handler(request, exc))
        self.assertEqual(resp.status_code, 422)

    def test_validation_error_strips_value_error_prefix(self) -> None:
        import json

        from fastapi.exceptions import RequestValidationError

        exc = RequestValidationError(
            errors=[
                {"loc": ("body", "amount"), "msg": "Value error, bad amount", "type": "value_error"}
            ]
        )
        resp = asyncio.run(validation_exception_handler(MagicMock(), exc))
        body = json.loads(resp.body)
        self.assertNotIn("Value error,", body["fields"][0]["message"])

    def test_validation_error_handles_missing_loc(self) -> None:
        import json

        from fastapi.exceptions import RequestValidationError

        exc = RequestValidationError(errors=[{"loc": (), "msg": "bad", "type": "value_error"}])
        resp = asyncio.run(validation_exception_handler(MagicMock(), exc))
        body = json.loads(resp.body)
        self.assertEqual(body["fields"][0]["field"], "unknown")
