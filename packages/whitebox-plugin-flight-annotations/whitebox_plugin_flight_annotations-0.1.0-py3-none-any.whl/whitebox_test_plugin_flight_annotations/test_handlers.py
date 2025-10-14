from unittest.mock import patch, AsyncMock, MagicMock
from django.test import TestCase

from whitebox_plugin_flight_annotations.handlers import (
    FlightAnnotationSendHandler,
    FlightAnnotationsLoadHandler,
)


class TestFlightAnnotationSendHandler(TestCase):
    @patch(
        "whitebox_plugin_flight_annotations.handlers.FlightAnnotationService.create_annotation"
    )
    @patch(
        "whitebox_plugin_flight_annotations.handlers.FlightAnnotationService.get_annotations_for_session"
    )
    @patch(
        "whitebox_plugin_flight_annotations.handlers.FlightAnnotationService._serialize_annotation"
    )
    async def test_handle_success(
        self, mock_serialize, mock_get_annotations, mock_create
    ):
        # GIVEN
        mock_annotation = MagicMock()
        mock_annotation.flight_session_id = 1
        mock_create.return_value = mock_annotation

        mock_annotations = [{"id": 1, "message": "test"}]
        mock_get_annotations.return_value = mock_annotations

        mock_serialized = {"id": 1, "message": "test", "author_name": "Test"}
        mock_serialize.return_value = mock_serialized

        handler = FlightAnnotationSendHandler()

        # WHEN
        result = await handler.handle(
            {"message": "Test message", "author_name": "Test Author"}
        )

        # THEN
        mock_create.assert_awaited_once_with(
            message="Test message", author_name="Test Author"
        )
        mock_get_annotations.assert_awaited_once_with(1)
        mock_serialize.assert_called_once_with(mock_annotation)

        expected = {
            "annotation": mock_serialized,
            "annotations": mock_annotations,
            "flight_session_id": 1,
        }
        self.assertEqual(result, expected)

    @patch("whitebox_plugin_flight_annotations.handlers.channel_layer")
    async def test_emit_annotation_list_with_session(self, mock_channel_layer):
        # GIVEN
        mock_channel_layer.group_send = AsyncMock()
        data = {}
        ctx = {"flight_session_id": 42, "annotations": [{"id": 1, "message": "test"}]}

        # WHEN
        await FlightAnnotationSendHandler.emit_annotation_list(data, ctx)

        # THEN
        mock_channel_layer.group_send.assert_awaited_once_with(
            "flight",
            {
                "type": "flight.annotations.list",
                "flight_session_id": 42,
                "annotations": [{"id": 1, "message": "test"}],
            },
        )


class TestFlightAnnotationsLoadHandler(TestCase):
    @patch("whitebox_plugin_flight_annotations.handlers.FlightService")
    @patch(
        "whitebox_plugin_flight_annotations.handlers.FlightAnnotationService.get_annotations_for_session"
    )
    async def test_handle_with_current_session(
        self, mock_get_annotations, mock_flight_service
    ):
        # GIVEN
        mock_flight_session = MagicMock()
        mock_flight_session.id = 42
        mock_flight_service.get_current_flight_session = AsyncMock(
            return_value=mock_flight_session
        )

        mock_annotations = [{"id": 1, "message": "test"}]
        mock_get_annotations.return_value = mock_annotations

        handler = FlightAnnotationsLoadHandler()

        # WHEN
        result = await handler.handle({})

        # THEN
        mock_flight_service.get_current_flight_session.assert_awaited_once()
        mock_get_annotations.assert_awaited_once_with(42)

        expected = {
            "annotations": mock_annotations,
            "flight_session_id": 42,
        }
        self.assertEqual(result, expected)

    @patch("whitebox_plugin_flight_annotations.handlers.channel_layer")
    async def test_emit_annotation_list_with_annotations(self, mock_channel_layer):
        # GIVEN
        mock_channel_layer.group_send = AsyncMock()
        data = {}
        ctx = {
            "flight_session_id": 42,
            "annotations": [
                {"id": 1, "message": "First message"},
                {"id": 2, "message": "Second message"},
            ],
        }

        # WHEN
        await FlightAnnotationsLoadHandler.emit_annotation_list(data, ctx)

        # THEN
        mock_channel_layer.group_send.assert_awaited_once_with(
            "flight",
            {
                "type": "flight.annotations.list",
                "flight_session_id": 42,
                "annotations": [
                    {"id": 1, "message": "First message"},
                    {"id": 2, "message": "Second message"},
                ],
            },
        )
