"""
Contains the Results endpoints (views)
"""
import django_rq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.serializers import JobResultSerializer


class ResultsView(APIView):
    def get(self, request, job_id, *args, **kwargs):
        """
        Returns the results of a job
        """
        # Get queue
        queue = django_rq.get_queue("default")
        # Fetch job
        job = queue.fetch_job(job_id)

        # If no job is found return 404
        if job is None:
            return Response(
                {"message": "Job not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch job status
        job_status = job.get_status()

        if job_status == "queued":
            return Response(
                {"message": "Your job is in queue"},
                status=status.HTTP_202_ACCEPTED,
            )

        if job_status == "failed":
            return Response(
                {"message": "Your job has failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if job_status == "started":
            return Response(
                {"message": "Your job has started"},
                status=status.HTTP_202_ACCEPTED,
            )

        if job_status == "deferred":
            return Response(
                {"message": "Your job is deferred"},
                status=status.HTTP_202_ACCEPTED,
            )

        # If we get here the job was sucessful
        # We can serialize the news
        serializer = JobResultSerializer(data=job.result)

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
