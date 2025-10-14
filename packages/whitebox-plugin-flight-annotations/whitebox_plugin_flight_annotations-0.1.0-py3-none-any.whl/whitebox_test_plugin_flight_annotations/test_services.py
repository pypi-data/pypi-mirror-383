from unittest.mock import patch, AsyncMock, MagicMock
from django.test.testcases import TransactionTestCase

from whitebox_plugin_flight_annotations.services import FlightAnnotationService


class TestFlightAnnotationService(TransactionTestCase):
    def setUp(self):
        # Mock the imports
        self.mock_annotation_model = MagicMock()
        self.mock_flight_service = MagicMock()

        # Mock the flight session
        self.mock_flight_session = MagicMock()
        self.mock_flight_session.id = 1
        self.mock_flight_session.is_active = True

    @patch("whitebox_plugin_flight_annotations.services.FlightAnnotation")
    @patch("whitebox_plugin_flight_annotations.services.FlightService")
    async def test_create_annotation_success(
        self, mock_flight_service, mock_annotation_model
    ):
        # GIVEN
        mock_flight_service.get_current_flight_session = AsyncMock(
            return_value=self.mock_flight_session
        )

        # Mock the created annotation
        mock_annotation = MagicMock()
        mock_annotation.id = 123
        mock_annotation.flight_session_id = 1
        mock_annotation_model.objects.acreate = AsyncMock(return_value=mock_annotation)

        # WHEN
        result = await FlightAnnotationService.create_annotation(
            message="Test message", author_name="Test Author"
        )

        # THEN
        mock_flight_service.get_current_flight_session.assert_awaited_once()
        mock_annotation_model.objects.acreate.assert_awaited_once_with(
            flight_session=self.mock_flight_session,
            message="Test message",
            author_name="Test Author",
        )
        self.assertEqual(result, mock_annotation)

    @patch("whitebox_plugin_flight_annotations.services.FlightService")
    async def test_get_annotations_for_session(self, mock_flight_service):
        # GIVEN
        mock_flight_service.get_current_flight_session = AsyncMock(return_value=None)

        # WHEN
        result = await FlightAnnotationService.get_annotations_for_session()

        # THEN
        self.assertEqual(result, [])

    def test_serialize_annotation(self):
        # GIVEN
        mock_annotation = MagicMock()
        mock_annotation.id = 123
        mock_annotation.message = "Test message"
        mock_annotation.author_name = "John Doe"
        mock_annotation.timestamp.isoformat.return_value = "2023-01-01T12:00:00"
        mock_annotation.flight_session_id = 42

        # WHEN
        result = FlightAnnotationService._serialize_annotation(mock_annotation)

        # THEN
        expected = {
            "id": 123,
            "message": "Test message",
            "author_name": "John Doe",
            "avatar_initial": "J",
            "timestamp": "2023-01-01T12:00:00",
            "flight_session_id": 42,
        }
        self.assertEqual(result, expected)

    def test_serialize_annotation_empty_author_name(self):
        """Test annotation serialization with empty author name"""
        # GIVEN
        mock_annotation = MagicMock()
        mock_annotation.id = 123
        mock_annotation.message = "Test message"
        mock_annotation.author_name = ""
        mock_annotation.timestamp.isoformat.return_value = "2023-01-01T12:00:00"
        mock_annotation.flight_session_id = 42

        # WHEN
        result = FlightAnnotationService._serialize_annotation(mock_annotation)

        # THEN
        self.assertEqual(result["avatar_initial"], "U")

    def test_serialize_annotation_none_author_name(self):
        # GIVEN
        mock_annotation = MagicMock()
        mock_annotation.id = 123
        mock_annotation.message = "Test message"
        mock_annotation.author_name = None
        mock_annotation.timestamp.isoformat.return_value = "2023-01-01T12:00:00"
        mock_annotation.flight_session_id = 42

        # WHEN
        result = FlightAnnotationService._serialize_annotation(mock_annotation)

        # THEN
        self.assertEqual(result["avatar_initial"], "U")
