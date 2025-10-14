from channels.layers import get_channel_layer

from whitebox import WebsocketEventHandler, import_whitebox_plugin_class
from whitebox.events import EventHandlerException
from .services import FlightAnnotationService


FlightService = import_whitebox_plugin_class("flight.FlightService")
channel_layer = get_channel_layer()


class FlightAnnotationSendHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.annotation.send` event.
    """

    @staticmethod
    async def emit_annotation_list(data, ctx):
        flight_session_id = ctx["flight_session_id"]
        annotations = ctx.get("annotations", [])

        if flight_session_id:
            await channel_layer.group_send(
                "flight",
                {
                    "type": "flight.annotations.list",
                    "flight_session_id": flight_session_id,
                    "annotations": annotations,
                },
            )

    default_callbacks = [
        emit_annotation_list,
    ]

    async def handle(self, data):
        message = data.get("message", "")
        author_name = data.get("author_name", "Unknown")

        try:
            # Create annotation using service
            annotation = await FlightAnnotationService.create_annotation(
                message=message, author_name=author_name
            )

            # Get updated list of annotations
            annotations = await FlightAnnotationService.get_annotations_for_session(
                annotation.flight_session_id
            )

        except ValueError as e:
            raise EventHandlerException(str(e))

        return {
            "annotation": FlightAnnotationService._serialize_annotation(annotation),
            "annotations": annotations,
            "flight_session_id": annotation.flight_session_id,
        }


class FlightAnnotationsLoadHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.annotations.load` event.
    """

    @staticmethod
    async def emit_annotation_list(data, ctx):
        flight_session_id = ctx["flight_session_id"]
        annotations = ctx.get("annotations", [])

        if flight_session_id:
            await channel_layer.group_send(
                "flight",
                {
                    "type": "flight.annotations.list",
                    "flight_session_id": flight_session_id,
                    "annotations": annotations,
                },
            )

    default_callbacks = [
        emit_annotation_list,
    ]

    async def handle(self, data):
        flight_session = await FlightService.get_current_flight_session()

        # Get annotations using service
        annotations = await FlightAnnotationService.get_annotations_for_session(
            flight_session.id
        )

        return {
            "annotations": annotations,
            "flight_session_id": flight_session.id,
        }
