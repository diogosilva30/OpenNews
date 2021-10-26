from celery.result import AsyncResult
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from core.serializers import NewsSerializer
from django.utils.timezone import now


class JobResultSerializer(serializers.Serializer):
    """
    Core job result serializer. Serializes the
    results from a particular job.
    """

    state = serializers.CharField()
    date_done = serializers.DateField()
    number_of_news = serializers.SerializerMethodField(read_only=True)
    news = NewsSerializer(many=True)

    def get_date(self, obj):
        return now()

    def get_number_of_news(self, obj):
        """
        `obj` is the dict created in `to_internal_value`.
        We acess `news` key.
        """
        return len(obj["news"])

    def to_internal_value(self, job: AsyncResult):

        # Check if state is 'PENDING'. If so, the task
        # is unknown (does not exist).
        if job.state == "PENDING":
            raise NotFound({"state": "NOT_FOUND"})

        # Try to get the result. If result is still None,
        # default to empty list
        news = job.result if job.result is not None else []

        return {
            "state": job.status,
            "news": news,
            "date_done": job.date_done,
        }
