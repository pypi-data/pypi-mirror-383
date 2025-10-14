import whitebox
from .handlers import FlightAnnotationSendHandler, FlightAnnotationsLoadHandler


class WhiteboxPluginFlightAnnotations(whitebox.Plugin):
    name = "Flight Annotations"

    slot_component_map = {
        "flight.annotations": "Annotations",
    }

    state_store_map = {
        "flight.annotations": "stores/annotations",
    }

    plugin_event_map = {
        "flight.annotation.send": FlightAnnotationSendHandler,
        "flight.annotations.load": FlightAnnotationsLoadHandler,
    }


plugin_class = WhiteboxPluginFlightAnnotations
