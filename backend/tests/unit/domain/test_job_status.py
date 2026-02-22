"""Tests for app.domain.entities.job.status.JobStatus."""

import unittest

from tests.common import BaseTestCase

from app.domain.entities.job.status import JobStatus


class JobStatusTestCase(BaseTestCase):
    """Global base class for ALL JobStatus tests."""

    def setUp(self) -> None:
        super().setUp()
        self.all_statuses = [
            JobStatus.PENDING,
            JobStatus.PROCESSING,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
        ]


class TestEnumValues(JobStatusTestCase):
    """Tests for enum member values."""

    def test_enum_values_pending(self) -> None:
        """
        When: Accessing PENDING value
        Then: Should be 'pending'
        """
        self.assertEqual(JobStatus.PENDING.value, "pending")

    def test_enum_values_processing(self) -> None:
        """
        When: Accessing PROCESSING value
        Then: Should be 'processing'
        """
        self.assertEqual(JobStatus.PROCESSING.value, "processing")

    def test_enum_values_completed(self) -> None:
        """
        When: Accessing COMPLETED value
        Then: Should be 'completed'
        """
        self.assertEqual(JobStatus.COMPLETED.value, "completed")

    def test_enum_values_failed(self) -> None:
        """
        When: Accessing FAILED value
        Then: Should be 'failed'
        """
        self.assertEqual(JobStatus.FAILED.value, "failed")

    def test_enum_values_total_count(self) -> None:
        """
        When: Counting all enum members
        Then: Should have exactly 4
        """
        self.assertEqual(len(JobStatus), 4)

    def test_enum_values_string_comparison(self) -> None:
        """
        When: Comparing enum member to string
        Then: Should be equal (str mixin)
        """
        self.assertEqual(JobStatus.PENDING, "pending")
        self.assertEqual(JobStatus.COMPLETED, "completed")

    def test_enum_values_can_iterate(self) -> None:
        """
        When: Iterating over JobStatus
        Then: Should yield all 4 members
        """
        values = [s.value for s in JobStatus]
        self.assertCountEqual(values, ["pending", "processing", "completed", "failed"])
