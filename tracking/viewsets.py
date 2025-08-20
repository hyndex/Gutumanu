from rest_framework import viewsets
from .models import LocationLog, GeofenceAlert, AIJob
from .serializers import TelemetrySerializer, AlertSerializer, AIJobSerializer


class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocationLog.objects.all().order_by('-timestamp')
    serializer_class = TelemetrySerializer


class AlertStreamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeofenceAlert.objects.all().order_by('-timestamp')
    serializer_class = AlertSerializer


class AIJobViewSet(viewsets.ModelViewSet):
    queryset = AIJob.objects.all().order_by('-created_at')
    serializer_class = AIJobSerializer
