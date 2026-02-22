"""Tests for app.infrastructure.notifications.tasks.document_tasks."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus


class HandleRejectedTest(BaseTestCase):
    """Tests for _handle_rejected()."""

    def test_handle_rejected_success_resets_to_draft(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_rejected

        doc = self.make_document(status=DocumentStatus.REJECTED.value)
        doc_repo = MagicMock()
        audit_repo = MagicMock()
        job_id = str(self.fake.uuid4())

        detail, succeeded = _handle_rejected(doc, doc_repo, audit_repo, job_id)

        self.assertTrue(succeeded)
        self.assertEqual(detail["action"], "reset_to_draft")
        doc_repo.update.assert_called_once_with(doc.id, {"status": DocumentStatus.DRAFT.value})
        audit_repo.log_state_change.assert_called_once()


class HandleDraftTest(BaseTestCase):
    """Tests for _handle_draft()."""

    def test_handle_draft_success_to_pending(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_draft

        doc = self.make_document(
            status=DocumentStatus.DRAFT.value,
            amount=Decimal("1000.00"),
            metadata={"client": self.fake.company(), "email": self.fake.email()},
        )
        doc_repo = MagicMock()
        audit_repo = MagicMock()
        job_id = str(self.fake.uuid4())

        detail, succeeded = _handle_draft(doc, doc_repo, audit_repo, job_id)

        self.assertTrue(succeeded)
        self.assertEqual(detail["status"], "success")
        doc_repo.update.assert_called_once()

    def test_handle_draft_success_to_rejected_amount_exceeds(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_draft

        doc = self.make_document(
            status=DocumentStatus.DRAFT.value,
            amount=Decimal("99_999_999.99"),
            metadata={"client": "C", "email": "e@e.com"},
        )
        doc_repo = MagicMock()
        audit_repo = MagicMock()
        job_id = str(self.fake.uuid4())

        detail, succeeded = _handle_draft(doc, doc_repo, audit_repo, job_id)

        self.assertTrue(succeeded)

    def test_handle_draft_success_to_rejected_missing_metadata(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_draft

        doc = self.make_document(
            status=DocumentStatus.DRAFT.value,
            amount=Decimal("100.00"),
            metadata={},
        )
        doc_repo = MagicMock()
        audit_repo = MagicMock()
        job_id = str(self.fake.uuid4())

        detail, succeeded = _handle_draft(doc, doc_repo, audit_repo, job_id)

        self.assertTrue(succeeded)

    def test_handle_draft_error_invalid_transition(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_draft

        doc = self.make_document(status=DocumentStatus.DRAFT.value, amount=Decimal("100.00"))
        doc_repo = MagicMock()
        audit_repo = MagicMock()
        job_id = str(self.fake.uuid4())

        with patch("app.domain.state_machine.StateMachine.validate_transition", return_value=False):
            detail, succeeded = _handle_draft(doc, doc_repo, audit_repo, job_id)

        self.assertFalse(succeeded)
        self.assertEqual(detail["status"], "failed")


class HandleFinalTest(BaseTestCase):
    """Tests for _handle_final()."""

    def test_handle_final_success_skips_approved(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_final

        doc = self.make_document(status=DocumentStatus.APPROVED.value)
        detail, succeeded = _handle_final(doc, MagicMock(), MagicMock(), str(self.fake.uuid4()))

        self.assertTrue(succeeded)
        self.assertEqual(detail["action"], "skipped")


class HandleUnknownTest(BaseTestCase):
    """Tests for _handle_unknown()."""

    def test_handle_unknown_error_unhandled_status(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _handle_unknown

        doc = self.make_document()
        doc.status = "weird_status"
        detail, succeeded = _handle_unknown(doc, MagicMock(), MagicMock(), str(self.fake.uuid4()))

        self.assertFalse(succeeded)
        self.assertIn("unhandled_status", detail["error"])


class BuildHandlersTest(BaseTestCase):
    """Tests for _build_handlers()."""

    def test_build_handlers_success_all_statuses(self) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _build_handlers

        handlers = _build_handlers()
        self.assertIn(DocumentStatus.DRAFT.value, handlers)
        self.assertIn(DocumentStatus.REJECTED.value, handlers)
        self.assertIn(DocumentStatus.APPROVED.value, handlers)
        self.assertIn(DocumentStatus.PENDING.value, handlers)


class ProcessDocumentsBatchTest(BaseTestCase):
    """Tests for process_documents_batch() Celery task."""

    @patch("app.infrastructure.notifications.tasks.document_tasks._notify_completion")
    @patch("app.infrastructure.notifications.tasks.document_tasks.SessionLocal")
    @patch("app.infrastructure.notifications.tasks.document_tasks.time.sleep")
    @patch("app.infrastructure.notifications.tasks.document_tasks.secrets.randbelow", return_value=0)
    def test_process_batch_success_all_documents(self, _rand, _sleep, mock_session_cls, _notify) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

        mock_db = self.make_mock_db_session()
        mock_session_cls.return_value = mock_db

        doc = self.make_document(status=DocumentStatus.DRAFT.value, metadata={"client": "C", "email": "e@e.com"})
        mock_job_repo = MagicMock()
        mock_doc_repo = MagicMock()
        mock_doc_repo.get_by_id.return_value = doc
        mock_audit_repo = MagicMock()

        with patch("app.infrastructure.repositories.job_repository.JobRepository", return_value=mock_job_repo), \
             patch("app.infrastructure.repositories.document_repository.DocumentRepository", return_value=mock_doc_repo), \
             patch("app.infrastructure.repositories.audit_repository.AuditRepository", return_value=mock_audit_repo):
            result = process_documents_batch(str(self.fake.uuid4()), [doc.id])

        self.assertEqual(result["total"], 1)

    @patch("app.infrastructure.notifications.tasks.document_tasks._notify_completion")
    @patch("app.infrastructure.notifications.tasks.document_tasks.SessionLocal")
    @patch("app.infrastructure.notifications.tasks.document_tasks.time.sleep")
    @patch("app.infrastructure.notifications.tasks.document_tasks.secrets.randbelow", return_value=0)
    def test_process_batch_success_document_not_found(self, _rand, _sleep, mock_session_cls, _notify) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

        mock_db = self.make_mock_db_session()
        mock_session_cls.return_value = mock_db

        mock_doc_repo = MagicMock()
        mock_doc_repo.get_by_id.return_value = None

        with patch("app.infrastructure.repositories.job_repository.JobRepository", return_value=MagicMock()), \
             patch("app.infrastructure.repositories.document_repository.DocumentRepository", return_value=mock_doc_repo), \
             patch("app.infrastructure.repositories.audit_repository.AuditRepository", return_value=MagicMock()):
            result = process_documents_batch(str(self.fake.uuid4()), [999])

        self.assertEqual(result["failed"], 1)

    @patch("app.infrastructure.notifications.tasks.document_tasks._notify_completion")
    @patch("app.infrastructure.notifications.tasks.document_tasks.SessionLocal")
    @patch("app.infrastructure.notifications.tasks.document_tasks.time.sleep")
    @patch("app.infrastructure.notifications.tasks.document_tasks.secrets.randbelow", return_value=0)
    def test_process_batch_error_document_exception(self, _rand, _sleep, mock_session_cls, _notify) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

        mock_db = self.make_mock_db_session()
        mock_session_cls.return_value = mock_db

        mock_doc_repo = MagicMock()
        mock_doc_repo.get_by_id.side_effect = Exception("db error")

        with patch("app.infrastructure.repositories.job_repository.JobRepository", return_value=MagicMock()), \
             patch("app.infrastructure.repositories.document_repository.DocumentRepository", return_value=mock_doc_repo), \
             patch("app.infrastructure.repositories.audit_repository.AuditRepository", return_value=MagicMock()):
            result = process_documents_batch(str(self.fake.uuid4()), [1])

        self.assertEqual(result["failed"], 1)

    @patch("app.infrastructure.notifications.tasks.document_tasks._notify_completion")
    @patch("app.infrastructure.notifications.tasks.document_tasks.SessionLocal")
    def test_process_batch_error_critical_failure(self, mock_session_cls, _notify) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

        mock_db = self.make_mock_db_session()
        mock_session_cls.return_value = mock_db

        mock_job_repo = MagicMock()
        mock_job_repo.update_status.side_effect = [Exception("fatal"), None]

        with patch("app.infrastructure.repositories.job_repository.JobRepository", return_value=mock_job_repo), \
             patch("app.infrastructure.repositories.document_repository.DocumentRepository", return_value=MagicMock()), \
             patch("app.infrastructure.repositories.audit_repository.AuditRepository", return_value=MagicMock()):
            with self.assertRaises(Exception):
                process_documents_batch(str(self.fake.uuid4()), [1])

    @patch("app.infrastructure.notifications.tasks.document_tasks._notify_completion")
    @patch("app.infrastructure.notifications.tasks.document_tasks.SessionLocal")
    def test_process_batch_error_critical_failure_update_also_fails(self, mock_session_cls, _notify) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

        mock_db = self.make_mock_db_session()
        mock_session_cls.return_value = mock_db

        mock_job_repo = MagicMock()
        mock_job_repo.update_status.side_effect = Exception("always fails")

        with patch("app.infrastructure.repositories.job_repository.JobRepository", return_value=mock_job_repo), \
             patch("app.infrastructure.repositories.document_repository.DocumentRepository", return_value=MagicMock()), \
             patch("app.infrastructure.repositories.audit_repository.AuditRepository", return_value=MagicMock()):
            with self.assertRaises(Exception):
                process_documents_batch(str(self.fake.uuid4()), [1])


    @patch("app.infrastructure.notifications.tasks.document_tasks._notify_completion")
    @patch("app.infrastructure.notifications.tasks.document_tasks.SessionLocal")
    @patch("app.infrastructure.notifications.tasks.document_tasks.time.sleep")
    @patch("app.infrastructure.notifications.tasks.document_tasks.secrets.randbelow", return_value=0)
    def test_process_batch_success_handler_returns_false(self, _rand, _sleep, mock_session_cls, _notify) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

        mock_db = self.make_mock_db_session()
        mock_session_cls.return_value = mock_db

        doc = self.make_document(status="unknown_status")

        mock_doc_repo = MagicMock()
        mock_doc_repo.get_by_id.return_value = doc

        with patch("app.infrastructure.repositories.job_repository.JobRepository", return_value=MagicMock()), \
             patch("app.infrastructure.repositories.document_repository.DocumentRepository", return_value=mock_doc_repo), \
             patch("app.infrastructure.repositories.audit_repository.AuditRepository", return_value=MagicMock()):
            result = process_documents_batch(str(self.fake.uuid4()), [doc.id])

        self.assertEqual(result["failed"], 1)


class NotifyCompletionTest(BaseTestCase):
    """Tests for _notify_completion()."""

    @patch("app.infrastructure.notifications.tasks.document_tasks.NotificationDispatcher")
    def test_notify_completion_success(self, mock_dispatcher_cls) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _notify_completion

        mock_result = MagicMock()
        mock_result.all_succeeded = True
        mock_dispatcher = MagicMock()
        mock_dispatcher.dispatch = MagicMock(return_value=mock_result)
        mock_dispatcher_cls.from_config.return_value = mock_dispatcher

        with patch("app.infrastructure.notifications.tasks.document_tasks.asyncio.run", return_value=mock_result):
            _notify_completion(
                job_id=str(self.fake.uuid4()),
                status="completed",
                document_ids=[1, 2],
                result={"total": 2, "processed": 2, "failed": 0, "details": []},
            )

    @patch("app.infrastructure.notifications.tasks.document_tasks.asyncio.run", side_effect=Exception("dispatch failed"))
    @patch("app.infrastructure.notifications.tasks.document_tasks.NotificationDispatcher")
    def test_notify_completion_error_exception_caught(self, _disp, _run) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _notify_completion

        _notify_completion(
            job_id=str(self.fake.uuid4()),
            status="failed",
            document_ids=[1],
            result={"total": 1, "processed": 0, "failed": 1, "details": []},
            error_message="critical error",
        )

    @patch("app.infrastructure.notifications.tasks.document_tasks.NotificationDispatcher")
    def test_notify_completion_success_partial_failure(self, mock_dispatcher_cls) -> None:
        from app.infrastructure.notifications.tasks.document_tasks import _notify_completion

        mock_result = MagicMock()
        mock_result.all_succeeded = False
        mock_result.succeeded = ["ch1"]
        mock_result.failed = ["ch2"]

        with patch("app.infrastructure.notifications.tasks.document_tasks.asyncio.run", return_value=mock_result):
            _notify_completion(
                job_id=str(self.fake.uuid4()),
                status="completed",
                document_ids=[1],
                result={"total": 1, "processed": 1, "failed": 0, "details": []},
            )
