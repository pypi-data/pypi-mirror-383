from typing import List, Optional

from .models import FlightAnnotation
from whitebox import import_whitebox_model, import_whitebox_plugin_class


FlightService = import_whitebox_plugin_class("flight.FlightService")


class FlightAnnotationService:
    """
    Service class for handling flight annotation related operations.
    """

    @classmethod
    async def create_annotation(
        cls,
        message: str,
        author_name: str,
        flight_session_id: Optional[int] = None,
    ):
        """
        Create a new flight annotation.

        Parameters:
            message: The annotation message.
            author_name: The name of the author.
            flight_session_id: The ID of the flight session. If None, uses current active session.

        Returns:
            The created FlightAnnotation object or None if no active session.
        """

        message = message.strip()
        author_name = author_name.strip()

        if not message:
            raise ValueError("Message cannot be empty")

        # Get flight session
        if flight_session_id:
            session = await FlightService.get_flight_session_by_id(flight_session_id)
        else:
            session = await FlightService.get_current_flight_session()

        if not session or not session.is_active:
            raise ValueError("No active flight session")

        # Create the annotation
        annotation = await FlightAnnotation.objects.acreate(
            flight_session=session,
            message=message,
            author_name=author_name,
        )

        return annotation

    @classmethod
    async def get_annotations_for_session(
        cls,
        flight_session_id: Optional[int] = None,
    ) -> List:
        """
        Get all annotations for a flight session.

        Parameters:
            flight_session_id: The ID of the flight session. If None, uses current active session.

        Returns:
            List of serialized annotations.
        """

        if not flight_session_id:
            # Get current flight session
            session = await FlightService.get_current_flight_session()
            if session:
                flight_session_id = session.id
            else:
                return []

        # Get all annotations for this flight session
        annotations = []
        async for annotation in FlightAnnotation.objects.filter(
            flight_session_id=flight_session_id
        ).order_by("timestamp"):
            annotations.append(cls._serialize_annotation(annotation))

        return annotations

    @classmethod
    def _serialize_annotation(cls, annotation):
        """
        Serialize annotation for WebSocket transmission
        """

        return {
            "id": annotation.id,
            "message": annotation.message,
            "author_name": annotation.author_name,
            "avatar_initial": annotation.author_name[0].upper()
            if annotation.author_name
            else "U",
            "timestamp": annotation.timestamp.isoformat(),
            "flight_session_id": annotation.flight_session_id,
        }
