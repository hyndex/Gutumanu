from rest_framework import serializers
from .models import LocationLog, GeofenceAlert, AIJob


class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationLog
        fields = ['id', 'child', 'latitude', 'longitude', 'accuracy', 'timestamp']


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeofenceAlert
        fields = ['id', 'child', 'triggered_type', 'latitude', 'longitude', 'radius', 'timestamp']


class AIJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIJob
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']
