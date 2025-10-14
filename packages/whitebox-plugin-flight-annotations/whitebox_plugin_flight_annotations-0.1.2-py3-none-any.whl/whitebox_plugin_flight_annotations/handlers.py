from channels.layers import get_channel_layer

from whitebox import WebsocketEventHandler, import_whitebox_plugin_class
from whitebox.events import EventHandlerException
from .serializers import AnnotationSerializer
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
                    "type": "flight.annotation.list",
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

        annotation_data = AnnotationSerializer(instance=annotation).data
        return {
            "annotation": annotation_data,
            "annotations": annotations,
            "flight_session_id": annotation.flight_session_id,
        }


class FlightAnnotationLoadHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.annotation.load` event.

    It's solely used to request the annotations by the client that's sending it.
    """

    response: dict = None

    async def handle(self, data):
        flight_session_id = data.get("flight_session_id")

        if flight_session_id:
            flight_session = await FlightService.get_flight_session_by_id(
                flight_session_id,
            )

        else:
            flight_session = await FlightService.get_current_flight_session()

        if not flight_session:
            raise EventHandlerException(
                f"No flight session with ID: {flight_session_id}"
                if flight_session_id
                else "No active flight session"
            )

        # Get annotations using service
        annotations = await FlightAnnotationService.get_annotations_for_session(
            flight_session.id,
        )

        result = {
            "annotations": annotations,
            "flight_session_id": flight_session.id,
        }
        # Make a copy of this response so that it's exactly what we return, as
        # the event apparatus may mutate the return value before passing it to
        # the websocket handler
        self.response = result.copy()

        return result

    async def return_message(self):
        return {
            "type": "flight.annotation.list",
            **self.response,
        }
