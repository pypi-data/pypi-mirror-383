from django.db import models
from django.utils import timezone


class FlightAnnotation(models.Model):
    """
    Model for storing flight annotations/comments during flight sessions.
    """

    # FIX: Using:
    # from whitebox import import_whitebox_model
    # FlightSession = import_whitebox_model("flight.FlightSession")
    # caused errors while creating migrations.
    # ImportError: cannot import name 'import_whitebox_model' from 'whitebox' (/app/whitebox/whitebox/__init__.py)

    flight_session = models.ForeignKey(
        "whitebox_plugin_flight_management.FlightSession",
        on_delete=models.CASCADE,
        related_name="annotations",
    )

    # Annotation content
    message = models.TextField()
    author_name = models.CharField(max_length=100, default="Unknown")

    # Timing
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Annotation by {self.author_name} at {self.timestamp}"
