from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracking/', include('tracking.urls')),  # Tracking app endpoints
    path('auth/', include('authapp.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
