"""Tests for app.domain.entities.job.job.Job."""

import unittest
from datetime import datetime
from uuid import UUID

from tests.common import BaseTestCase

from app.domain.entities.job.job import Job
from app.domain.entities.job.status import JobStatus


class JobTestCase(BaseTestCase):
    """Global base class for ALL Job tests."""

    def setUp(self) -> None:
        super().setUp()
        self.valid_document_ids = [self.fake.random_int(min=1, max=999) for _ in range(3)]

    def get_instance(self, **overrides: object) -> Job:
        defaults = {
            "document_ids": self.valid_document_ids,
        }
        defaults.update(overrides)
        return Job(**defaults)


class TestUnderScoreUnderScoreInit(JobTestCase):
    """Tests for __init__()."""

    def test_init_success_valid_params(self) -> None:
        """
        When: Job is created with valid parameters
        Then: Should set all attributes correctly
        """
        job = self.get_instance()

        self.assertIsInstance(job.id, UUID)
        self.assertEqual(job.document_ids, self.valid_document_ids)
        self.assertEqual(job.status, JobStatus.PENDING.value)
        self.assertIsNotNone(job.created_at)
        self.assertIsNone(job.completed_at)
        self.assertIsNone(job.error_message)
        self.assertIsNone(job.result)

    def test_init_success_with_custom_id(self) -> None:
        """
        When: Job is created with explicit UUID
        Then: Should use provided UUID
        """
        job = self.get_instance(id=self.test_uuid)
        self.assertEqual(job.id, self.test_uuid)

    def test_init_success_auto_generated_id(self) -> None:
        """
        When: Job is created without explicit ID
        Then: Should auto-generate a UUID
        """
        job1 = self.get_instance()
        job2 = self.get_instance()
        self.assertNotEqual(job1.id, job2.id)

    def test_init_success_defaults(self) -> None:
        """
        When: Job is created with only required params
        Then: Should use default values
        """
        doc_id = self.fake.random_int(min=1, max=999)
        job = Job(document_ids=[doc_id])
        self.assertEqual(job.status, JobStatus.PENDING.value)
        self.assertIsNone(job.completed_at)
        self.assertIsNone(job.error_message)
        self.assertIsNone(job.result)

    def test_init_success_single_document(self) -> None:
        """
        When: Job is created for a single document
        Then: Should work correctly
        """
        single_id = self.fake.random_int(min=1, max=999)
        job = self.get_instance(document_ids=[single_id])
        self.assertEqual(job.document_ids, [single_id])


class TestStartProcessing(JobTestCase):
    """Tests for start_processing()."""

    def test_start_processing_success_from_pending(self) -> None:
        """
        When: Job starts processing from PENDING
        Then: Should set status to PROCESSING
        """
        job = self.get_instance()
        job.start_processing()
        self.assertEqual(job.status, JobStatus.PROCESSING.value)

    def test_start_processing_success_preserves_other_fields(self) -> None:
        """
        When: Job starts processing
        Then: Should not modify other fields
        """
        job = self.get_instance()
        original_id = job.id
        original_docs = job.document_ids

        job.start_processing()

        self.assertEqual(job.id, original_id)
        self.assertEqual(job.document_ids, original_docs)
        self.assertIsNone(job.completed_at)

    def test_start_processing_success_idempotent(self) -> None:
        """
        When: start_processing() is called multiple times
        Then: Should remain in PROCESSING state
        """
        job = self.get_instance()
        job.start_processing()
        job.start_processing()
        self.assertEqual(job.status, JobStatus.PROCESSING.value)


class TestComplete(JobTestCase):
    """Tests for complete()."""

    def test_complete_success_with_result(self) -> None:
        """
        When: Job is completed with result data
        Then: Should set status, completed_at, and result
        """
        job = self.get_instance()
        job.start_processing()
        result = {"total": 3, "processed": 3, "failed": 0}

        job.complete(result)

        self.assertEqual(job.status, JobStatus.COMPLETED.value)
        self.assertIsNotNone(job.completed_at)
        self.assertEqual(job.result, result)
        self.assertIsNone(job.error_message)

    def test_complete_success_clears_error_message(self) -> None:
        """
        When: Job completes successfully after having an error message
        Then: Should clear the error_message
        """
        job = self.get_instance()
        job.error_message = self.fake.sentence()

        job.complete({"total": 1, "processed": 1, "failed": 0})

        self.assertIsNone(job.error_message)

    def test_complete_success_sets_timestamp(self) -> None:
        """
        When: Job is completed
        Then: completed_at should be a valid datetime
        """
        job = self.get_instance()
        job.complete({"total": 1})

        self.assertIsInstance(job.completed_at, datetime)

    def test_complete_success_empty_result(self) -> None:
        """
        When: Job completes with empty result dict
        Then: Should still set completed status
        """
        job = self.get_instance()
        job.complete({})

        self.assertEqual(job.status, JobStatus.COMPLETED.value)
        self.assertEqual(job.result, {})

    def test_complete_success_preserves_document_ids(self) -> None:
        """
        When: Job is completed
        Then: Should not modify document_ids
        """
        job = self.get_instance()
        original_docs = job.document_ids.copy()

        job.complete({"done": True})

        self.assertEqual(job.document_ids, original_docs)


class TestFail(JobTestCase):
    """Tests for fail()."""

    def test_fail_success_with_message(self) -> None:
        """
        When: Job fails with an error message
        Then: Should set FAILED status and error_message
        """
        job = self.get_instance()
        job.start_processing()

        error_msg = self.fake.sentence()
        job.fail(error_msg)

        self.assertEqual(job.status, JobStatus.FAILED.value)
        self.assertEqual(job.error_message, error_msg)
        self.assertIsNotNone(job.completed_at)

    def test_fail_success_sets_completed_at(self) -> None:
        """
        When: Job fails
        Then: Should set completed_at timestamp
        """
        job = self.get_instance()
        job.fail(self.fake.sentence())

        self.assertIsInstance(job.completed_at, datetime)

    def test_fail_success_preserves_document_ids(self) -> None:
        """
        When: Job fails
        Then: Should not modify document_ids
        """
        job = self.get_instance()
        original_docs = job.document_ids.copy()

        job.fail(self.fake.sentence())

        self.assertEqual(job.document_ids, original_docs)


class TestIsCompleted(JobTestCase):
    """Tests for is_completed()."""

    def test_is_completed_success_completed_status(self) -> None:
        """
        When: Job has COMPLETED status
        Then: Should return True
        """
        job = self.get_instance()
        job.complete({"done": True})
        self.assertTrue(job.is_completed())

    def test_is_completed_success_failed_status(self) -> None:
        """
        When: Job has FAILED status
        Then: Should return True (finished with failure)
        """
        job = self.get_instance()
        job.fail(self.fake.sentence())
        self.assertTrue(job.is_completed())

    def test_is_completed_error_pending_status(self) -> None:
        """
        When: Job is in PENDING status
        Then: Should return False
        """
        job = self.get_instance()
        self.assertFalse(job.is_completed())

    def test_is_completed_error_processing_status(self) -> None:
        """
        When: Job is in PROCESSING status
        Then: Should return False
        """
        job = self.get_instance()
        job.start_processing()
        self.assertFalse(job.is_completed())


class TestIsProcessing(JobTestCase):
    """Tests for is_processing()."""

    def test_is_processing_success_processing_status(self) -> None:
        """
        When: Job is in PROCESSING status
        Then: Should return True
        """
        job = self.get_instance()
        job.start_processing()
        self.assertTrue(job.is_processing())

    def test_is_processing_error_pending_status(self) -> None:
        """
        When: Job is in PENDING status
        Then: Should return False
        """
        job = self.get_instance()
        self.assertFalse(job.is_processing())

    def test_is_processing_error_completed_status(self) -> None:
        """
        When: Job is COMPLETED
        Then: Should return False
        """
        job = self.get_instance()
        job.complete({"done": True})
        self.assertFalse(job.is_processing())

    def test_is_processing_error_failed_status(self) -> None:
        """
        When: Job is FAILED
        Then: Should return False
        """
        job = self.get_instance()
        job.fail(self.fake.sentence())
        self.assertFalse(job.is_processing())


class TestUnderScoreUnderScoreRepr(JobTestCase):
    """Tests for __repr__()."""

    def test_repr_success_contains_status(self) -> None:
        """
        When: repr() is called on a Job
        Then: Should include status
        """
        job = self.get_instance()
        result = repr(job)
        self.assertIn("pending", result)

    def test_repr_success_contains_doc_count(self) -> None:
        """
        When: repr() is called on a Job
        Then: Should include document count
        """
        job = self.get_instance()
        result = repr(job)
        self.assertIn("3", result)

    def test_repr_success_format(self) -> None:
        """
        When: repr() is called
        Then: Should follow expected format
        """
        job = self.get_instance()
        result = repr(job)
        self.assertTrue(result.startswith("Job("))
