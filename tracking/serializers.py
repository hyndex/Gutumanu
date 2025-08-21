from rest_framework import serializers
from .models import LocationLog, GeofenceAlert, AIJob, InferenceRun


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


class InferenceRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceRun
        fields = ['id', 'job', 'model_name', 'score', 'latency_ms', 'accuracy', 'drift', 'created_at']
