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

    # Id of job
    id = serializers.CharField()
    # State of the job
    state = serializers.CharField()
    date_done = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    # Original job keyword arguments
    job_arguments = serializers.DictField()
    number_of_news = serializers.SerializerMethodField(read_only=True)
    news = NewsSerializer(many=True)

    def __init__(self, *args, **kwargs):
        """
        Override __init__ for dynamic field serialization.
        When the job state is not "SUCESS" (not done), we only serialize
        the job `id`, `state` and `job_arguments`
        """
        # Instantiate the superclass normally
        super(JobResultSerializer, self).__init__(*args, **kwargs)

        if self.fields["state"] == "WAITING":
            allowed = ["id", "state"]
        if self.fields["state"] == "STARTED":
            allowed = ["id", "state", "job_arguments"]
        if self.fields["state"] == "SUCCESS":
            allowed = self.fields

        allowed = set(allowed)
        existing = set(self.fields)
        for field_name in existing - allowed:
            self.fields.pop(field_name)

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

        import datetime

        if job.date_done:
            expires = job.date_done + datetime.timedelta(
                seconds=job.backend.expires
            )
        else:
            expires = None
        return {
            "id": job.id,
            "state": job.status,
            "news": news,
            "date_done": job.date_done,
            "job_arguments": job.kwargs,
            "expires_at": expires,
        }
