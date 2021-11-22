"""
Module containing the serializer classes for the results endpoint.
"""
import datetime
from celery.result import AsyncResult
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from core.serializers import NewsSerializer


class JobResultSerializer(serializers.Serializer):
    """
    Core job result serializer. Serializes the
    results from a particular job.
    """

    # Id of job (always present in deserialization)
    id = serializers.CharField(required=True)
    # State of the job (always present in deserialization)
    state = serializers.CharField(required=True)
    # Traceback in case of failed task (only present if task fails)
    traceback = serializers.CharField(required=False)
    # Timestamp of when the job was completed (might be omitted in deserialization)
    date_done = serializers.DateTimeField(required=False)
    # Timestamp of when the job will expire (might be omitted in deserialization)
    expires_at = serializers.DateTimeField(required=False)
    # Original job keyword arguments (might be omitted in deserialization)
    job_arguments = serializers.DictField(required=False)
    # Number of found news (might be omitted in deserialization)
    number_of_news = serializers.SerializerMethodField(read_only=True)
    # The list of found news (might be omitted in deserialization)
    news = NewsSerializer(many=True, required=False, allow_null=True)

    def get_number_of_news(self, obj):
        """
        `obj` is the dict created in `to_internal_value`.
        We acess `news` key.
        """
        news = obj.get("news", None)
        return len(news) if news else None

    def to_internal_value(self, job: AsyncResult):

        # Define the inital data (these fields are always present in deserialization)
        data = {"id": job.id, "state": job.state}

        # Check if state is 'PENDING'. If so, the task
        # is unknown (does not exist).
        if job.state == "PENDING":
            raise NotFound({"id": job.id, "state": "NOT_FOUND"})

        # If job failed, include the traceback
        if job.state == "FAILURE":
            data |= {"traceback": job.traceback}

        # If job is 'STARTED', or 'FAILURE' include 'job_arguments'
        if job.state in ["STARTED", "FAILURE"]:
            data |= {"job_arguments": job.kwargs}

        # If job is 'SUCCESS' include every field
        if job.state == "SUCCESS":
            data |= {
                "job_arguments": job.kwargs,
                "date_done": job.date_done,
                "expires_at": (
                    job.date_done
                    + datetime.timedelta(seconds=job.backend.expires)
                ),
                "news": job.result.news,  # result is of type 'NewsFactory'
            }

        return data
