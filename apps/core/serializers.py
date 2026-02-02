"""Core serializers."""
from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField()
    database = serializers.BooleanField()
    cache = serializers.BooleanField()
