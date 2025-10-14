import whitebox
from .handlers import (
    FlightAnnotationSendHandler,
    FlightAnnotationLoadHandler,
)


class WhiteboxPluginFlightAnnotations(whitebox.Plugin):
    name = "Flight Annotations"

    slot_component_map = {
        "flight.annotations": "Annotations",
        "flight.annotations-overlay": "AnnotationsOverlay",
    }

    state_store_map = {
        "flight.annotations": "stores/annotations",
    }

    plugin_event_map = {
        "flight.annotation.send": FlightAnnotationSendHandler,
        "flight.annotation.load": FlightAnnotationLoadHandler,
    }

    exposed_component_map = {
        "service-component": {
            "annotations": "AnnotationsServiceComponent",
        },
    }


plugin_class = WhiteboxPluginFlightAnnotations
