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
        # Get job
        job = AsyncResult(job_id)

        # Pass job to serializer
        serializer = self.get_serializer(data=job)

        # Check for errors (raise 400 bad request if any error)
        serializer.is_valid(raise_exception=True)

        # If serializer is valid we return a 200 response with the
        # serializer data
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
