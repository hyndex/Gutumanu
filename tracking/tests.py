from django.test import TestCase
from .models import Child, LocationLog, IPLog, DeviceInfoLog
from django.urls import reverse
import json
from django.contrib.auth.models import User

class ModelTests(TestCase):
    def test_child_creation(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        self.assertEqual(child.auth_token, '')
        self.assertIsNotNone(child.created_at)

    def test_location_log_creation(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        log = LocationLog.objects.create(
            child=child,
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=10.5
        )
        self.assertEqual(log.latitude, 40.7128)
        self.assertEqual(log.accuracy, 10.5)

class ViewTests(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user('testparent')
        self.child = Child.objects.create(
            name='Test Child',
            device_id='test-device-123',
            parent=self.parent,
            auth_token='valid-test-token'
        )

    def test_child_creation(self):
        child = Child.objects.create(
            name='Test Child', 
            device_id='unique-device-456',
            parent=self.parent,
            auth_token='another-token'
        )
        self.assertEqual(child.auth_token, '')
        self.assertIsNotNone(child.created_at)

    def test_update_location_view(self):
        url = reverse('update_location')
        data = {
            'device_id': 'test-device-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'accuracy': 10.5
        }
        response = self.client.post(
            url, 
            json.dumps(data), 
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='test-token-456'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LocationLog.objects.count(), 1)

    def test_invalid_token(self):
        url = reverse('update_location')
        data = {'device_id': 'test-device-123'}
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='wrong-token'
        )
        self.assertEqual(response.status_code, 403)
    def test_ip_log_creation(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        log = IPLog.objects.create(
            child=child,
            ip_address='192.168.1.1',
            details='Test network info'
        )
        self.assertEqual(log.ip_address, '192.168.1.1')

    def test_device_info_log_creation(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        log = DeviceInfoLog.objects.create(
            child=child,
            user_agent='Test Browser',
            platform='Windows',
            screen_width=1024,
            screen_height=768
        )
        self.assertEqual(log.platform, 'Windows')

    def test_update_ip_view(self):
        url = reverse('update_ip')
        data = {
            'device_id': 'test-device-123',
            'ip_address': '192.168.1.100',
            'details': 'Test network'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='test-token-456'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(IPLog.objects.count(), 1)

    def test_invalid_ip_data(self):
        url = reverse('update_ip')
        response = self.client.post(
            url,
            json.dumps({'invalid': 'data'}),
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='test-token-456'
        )
        self.assertEqual(response.status_code, 400)

    def test_duplicate_log_prevention(self):
        url = reverse('update_location')
        data = {'device_id': self.child.device_id, 'latitude': 40.7128}
        # First request
        self.client.post(url, json.dumps(data), content_type='application/json',
                        HTTP_X_DEVICE_ID='test-device-123',
                        HTTP_X_AUTH_TOKEN='test-token-456')
        # Second identical request
        response = self.client.post(url, json.dumps(data), content_type='application/json',
                                   HTTP_X_DEVICE_ID='test-device-123',
                                   HTTP_X_AUTH_TOKEN='test-token-456')
        self.assertEqual(LocationLog.objects.count(), 1)
        self.assertIn('error', json.loads(response.content))

    def test_call_log_creation(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        log = CallLog.objects.create(
            child=child,
            number='123456789',
            duration=60,
            type='outgoing'
        )
        self.assertEqual(log.type, 'outgoing')

    def test_submit_call_log_view(self):
        url = reverse('submit_call_log')
        data = {
            'device_id': 'test-device-123',
            'number': '123456789',
            'duration': 60,
            'type': 'outgoing'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='test-token-456'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CallLog.objects.count(), 1)

    def test_invalid_call_log_data(self):
        url = reverse('submit_call_log')
        response = self.client.post(
            url,
            json.dumps({'invalid': 'data'}),
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='test-token-456'
        )
        self.assertEqual(response.status_code, 400)

    def test_social_media_log_validation(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        log = SocialMediaLog.objects.create(
            child=child,
            platform='Instagram',
            content='Test message',
            sender='test_user'
        )
        self.assertEqual(log.platform, 'Instagram')

    def test_social_media_missing_fields(self):
        child = Child.objects.create(name='Test Child', device_id='test-device-123', parent=User.objects.create_user('testuser'))
        with self.assertRaises(ValueError):
            SocialMediaLog.objects.create(
                child=child,
                platform='Instagram',
                # Missing 'content' field
                sender='test_user'
            )

    def test_ip_log_duplicate_prevention(self):
        url = reverse('update_ip')
        data = {
            'device_id': 'test-device-123',
            'ip_address': '192.168.1.100',
            'details': 'Test network'
        }
        # First request
        self.client.post(url, json.dumps(data), content_type='application/json',
                        HTTP_X_DEVICE_ID='test-device-123',
                        HTTP_X_AUTH_TOKEN='test-token-456')
        # Second identical request
        response = self.client.post(url, json.dumps(data), content_type='application/json',
                                   HTTP_X_DEVICE_ID='test-device-123',
                                   HTTP_X_AUTH_TOKEN='test-token-456')
        self.assertEqual(IPLog.objects.count(), 1)
        self.assertIn('error', json.loads(response.content))

    def test_invalid_http_methods(self):
        url = reverse('update_location')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_auth_token_renewal(self):
        url = reverse('token-renew')
        response = self.client.post(url, 
            json.dumps({'device_id': 'test-device-123'}),
            content_type='application/json',
            HTTP_X_DEVICE_ID='test-device-123',
            HTTP_X_AUTH_TOKEN='test-token-456'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('new_token', json.loads(response.content))

    def test_missing_auth_headers(self):
        url = reverse('update_location')
        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 403)
