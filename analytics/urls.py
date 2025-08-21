from django.urls import path
from .views import AnalyticsJobListCreateView, AnalyticsJobDetailView

urlpatterns = [
    path('v1/analytics/jobs', AnalyticsJobListCreateView.as_view(), name='analytics-job-create'),
    path('v1/analytics/jobs/<uuid:job_id>', AnalyticsJobDetailView.as_view(), name='analytics-job-detail'),
]
