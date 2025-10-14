from django.test import TestCase

from plugin.manager import plugin_manager
from whitebox_plugin_flight_annotations.handlers import (
    FlightAnnotationSendHandler,
    FlightAnnotationsLoadHandler,
)


class TestWhiteboxPluginFlightAnnotations(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginFlightAnnotations"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        """Test that the plugin is properly loaded"""
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        """Test plugin has correct name"""
        self.assertEqual(self.plugin.name, "Flight Annotations")
