from django.urls import path
from tracking.consumers import AlertConsumer

websocket_urlpatterns = [
    path('ws/alerts/', AlertConsumer.as_asgi()),
]
