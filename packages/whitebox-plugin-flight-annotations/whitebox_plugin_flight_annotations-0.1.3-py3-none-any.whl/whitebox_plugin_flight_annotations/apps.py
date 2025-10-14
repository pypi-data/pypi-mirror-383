from django.apps import AppConfig

from plugin.registry import model_registry


class WhiteboxPluginFlightAnnotationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whitebox_plugin_flight_annotations"
    verbose_name = "Flight Annotations"

    def ready(self):
        from .models import FlightAnnotation

        model_registry.register("flight.FlightAnnotation", FlightAnnotation)
