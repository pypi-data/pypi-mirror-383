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
