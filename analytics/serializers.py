from rest_framework import serializers
from .models import AnalyticsJob


class AnalyticsJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsJob
        fields = ['id', 'sql_query', 'status', 'result_s3_uri', 'created_at']
        read_only_fields = ['id', 'status', 'result_s3_uri', 'created_at']


class AnalyticsJobCreateSerializer(serializers.Serializer):
    sql_query = serializers.CharField()
