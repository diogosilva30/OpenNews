from celery.result import AsyncResult
from rest_framework import serializers
from core.serializers import NewsSerializer
from django.utils.timezone import now


class JobResultSerializer(serializers.Serializer):
    """
    Core job result serializer. Serializes the
    results from a particular job.
    """

    status = serializers.CharField()
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

        from pprint import pprint

        print(job.status)
        if job.result is None:
            news = []
        else:
            news = job.result
        # serializer = NewsSerializer(data=data, many=True)
        # if serializer.is_valid():
        return {"status": job.status, "news": news, "date_done": job.date_done}

        raise ValueError(serializer.errors)
