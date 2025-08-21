from rest_framework import status
import uuid
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import AnalyticsJob
from .serializers import AnalyticsJobSerializer, AnalyticsJobCreateSerializer


class AnalyticsJobListCreateView(APIView):
    def post(self, request):
        serializer = AnalyticsJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = AnalyticsJob.objects.create(
            sql_query=serializer.validated_data['sql_query'],
            result_s3_uri=f"s3://results/{uuid.uuid4()}.parquet",
            status='completed',
        )
        return Response({'id': str(job.id)}, status=status.HTTP_201_CREATED)


class AnalyticsJobDetailView(APIView):
    def get(self, request, job_id):
        job = get_object_or_404(AnalyticsJob, id=job_id)
        serializer = AnalyticsJobSerializer(job)
        return Response(serializer.data)
