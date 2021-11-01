"""
Contains the Results endpoints (views)
"""
from rest_framework.response import Response
from rest_framework import generics, mixins, status
from celery.result import AsyncResult


from .serializers import JobResultSerializer


class ResultsView(
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    serializer_class = JobResultSerializer

    def get(self, request, job_id, *args, **kwargs):
        """
        Returns the results of a job
        """
        job = AsyncResult(job_id)

        serializer = self.get_serializer(data=job)

        if serializer.is_valid():
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
