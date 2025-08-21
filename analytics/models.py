import uuid
from django.db import models


class AnalyticsJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sql_query = models.TextField()
    status = models.CharField(max_length=32, default='completed')
    result_s3_uri = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
