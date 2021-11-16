from celery.result import AsyncResult
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.utils.timezone import now

from core.models import NewsFactory
from core.serializers import NewsSerializer


class JobResultSerializer(serializers.Serializer):
    """
    Core job result serializer. Serializes the
    results from a particular job.
    """

    # State of the job
    state = serializers.CharField()
    # Original job keyword arguments
    job_arguments = serializers.DictField()
    date_done = serializers.DateTimeField()
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

        # Try to get the news factory.
        news_factory = job.result

        # If news factory is not actually a news factory instance, we dont have results yet,
        # so we default the collected news to a empty list.
        # Otherwise collect news from factory.
        if isinstance(news_factory, NewsFactory):
            news = news_factory.news
        else:
            news = []

        return {
            "state": job.status,
            "news": news,
            "date_done": job.date_done,
            "job_arguments": job.kwargs,
        }
