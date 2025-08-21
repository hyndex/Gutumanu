"""Test suite for the tracking application models and serializers."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Child, LocationLog, SMSLog, GeofenceAlert
from .serializers import TelemetrySerializer, AlertSerializer


class UniquenessTests(TestCase):
    """Ensure ``UniqueConstraint`` definitions work as expected."""

    def setUp(self):
        parent = User.objects.create_user(username="parent")
        self.child = Child.objects.create(name="Kid", device_id="dev-1", parent=parent)

    def test_location_log_unique_constraint(self):
        log = LocationLog.objects.create(
            child=self.child, latitude=1.0, longitude=2.0
        )
        with self.assertRaises(ValidationError):
            LocationLog.objects.create(
                child=self.child,
                latitude=1.0,
                longitude=2.0,
                timestamp=log.timestamp,
            )

    def test_sms_log_unique_constraint(self):
        sms = SMSLog.objects.create(
            child=self.child, message="hello", direction="sent"
        )
        with self.assertRaises(ValidationError):
            SMSLog.objects.create(
                child=self.child,
                message="hello",
                direction="sent",
                timestamp=sms.timestamp,
            )


class SerializationTests(TestCase):
    """Verify that serializers output the expected data."""

    def setUp(self):
        parent = User.objects.create_user(username="parent2")
        self.child = Child.objects.create(name="Kiddo", device_id="dev-2", parent=parent)

    def test_telemetry_serializer(self):
        log = LocationLog.objects.create(
            child=self.child, latitude=3.0, longitude=4.0, accuracy=5.0
        )
        data = TelemetrySerializer(log).data
        self.assertEqual(data["child"], self.child.id)
        self.assertEqual(data["latitude"], 3.0)

    def test_alert_serializer(self):
        alert = GeofenceAlert.objects.create(
            child=self.child,
            latitude=5.0,
            longitude=6.0,
            radius=10.0,
            triggered_type="entry",
        )
        data = AlertSerializer(alert).data
        self.assertEqual(data["child"], self.child.id)
        self.assertEqual(data["radius"], 10.0)
