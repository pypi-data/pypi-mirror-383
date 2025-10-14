from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock

from whitebox_plugin_flight_annotations.models import FlightAnnotation


class TestFlightAnnotationModel(TestCase):
    def setUp(self):
        # Mock flight session since we can't create real ones in unit tests
        self.mock_flight_session = MagicMock()
        self.mock_flight_session.id = 1
        self.mock_flight_session.pk = 1

    def test_flight_annotation_creation(self):
        # GIVEN
        test_message = "This is a test annotation"
        test_author = "Test Pilot"
        test_time = timezone.now()

        # WHEN
        annotation = FlightAnnotation(
            flight_session_id=self.mock_flight_session.id,
            message=test_message,
            author_name=test_author,
            timestamp=test_time,
        )

        # THEN
        self.assertEqual(annotation.flight_session_id, 1)
        self.assertEqual(annotation.message, test_message)
        self.assertEqual(annotation.author_name, test_author)
        self.assertEqual(annotation.timestamp, test_time)

    def test_flight_annotation_default_values(self):
        # WHEN
        annotation = FlightAnnotation(
            flight_session_id=self.mock_flight_session.id,
            message="Test message",
            # author_name should default to "Unknown"
            # timestamp should default to timezone.now()
        )

        # THEN
        self.assertEqual(annotation.author_name, "Unknown")
        self.assertIsNotNone(annotation.timestamp)
        # Check that timestamp is recent (within last minute)
        time_diff = timezone.now() - annotation.timestamp
        self.assertTrue(time_diff.total_seconds() < 60)
