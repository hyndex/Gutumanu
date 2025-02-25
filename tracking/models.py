from django.db import models
from django.contrib.auth.models import User

class Child(models.Model):
    """
    Represents a tracked child or device.
    """
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    safe_zone = models.TextField(
        blank=True,
        help_text="Optional: JSON defining safe zone coordinates"
    )
    update_interval = models.PositiveIntegerField(
        default=60,
        help_text="Update interval in seconds for tracking data"
    )

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    def latest_location(self):
        return self.locations.order_by('-timestamp').first()

    def latest_location_map_link(self):
        loc = self.latest_location()
        if loc:
            return f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}"
        return None

class LocationLog(models.Model):
    """
    Stores GPS tracking data.
    """
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='locations')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.child.name} @ {self.timestamp}"

class IPLog(models.Model):
    """
    Stores IP address and network information.
    """
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='ip_logs')
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.child.name} IP: {self.ip_address} at {self.timestamp}"

class DeviceInfoLog(models.Model):
    """
    Stores browser and device information.
    """
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='device_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField()
    platform = models.CharField(max_length=100)
    screen_width = models.IntegerField()
    screen_height = models.IntegerField()
    other_details = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.child.name} device info at {self.timestamp}"

class PhotoCapture(models.Model):
    """
    Stores images captured from the webcam.
    """
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='captures/')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Photo for {self.child.name} at {self.timestamp}"

class SensorDataLog(models.Model):
    """
    Stores sensor data from the device (accelerometer, gyroscope, ambient light, etc.).
    """
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='sensor_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(
        blank=True, 
        null=True,
        help_text="JSON data from sensors (e.g., accelerometer, gyroscope, ambient light)"
    )

    def __str__(self):
        return f"Sensor data for {self.child.name} at {self.timestamp}"

class PermissionLog(models.Model):
    """
    Stores permission statuses for various browser APIs.
    """
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

    def __str__(self):
        return f"Permission log for {self.child.name} at {self.timestamp}"
