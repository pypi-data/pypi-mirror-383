from rest_framework import serializers

from .models import FlightAnnotation


class AnnotationSerializer(serializers.ModelSerializer):
    avatar_initial = serializers.SerializerMethodField()

    class Meta:
        model = FlightAnnotation
        fields = [
            "id",
            "message",
            "author_name",
            "avatar_initial",
            "timestamp",
            "flight_session_id",
        ]

    def get_avatar_initial(self, annotation):
        return annotation.author_name[0].upper()
