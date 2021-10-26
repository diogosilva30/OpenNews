"""
Core views
"""
from abc import abstractstaticmethod
from celery.app import shared_task
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, generics, status
from rest_framework.response import Response

from .serializers import (
    JobSerializer,
    KeywordSearchSerializer,
    URLSearchSerializer,
    TagSearchSerializer,
)
from .models import NewsFactory


class BaseJobCreationView(mixins.CreateModelMixin, generics.GenericAPIView):
    # Child views must define a news Factory class
    news_factory_class: NewsFactory = None

    # Child views must define a serializer class
    serializer_class = None

    @abstractstaticmethod
    def celery_job(factory_cls: NewsFactory, **job_kwargs):
        """
        Child classes must implement this static method to create
        a celery job.
        """

    @swagger_auto_schema(responses={201: JobSerializer()})
    def post(self, request, *args, **kwargs):
        # Create serializer from request data
        serializer = self.get_serializer(data=request.data)

        # Check for request errors
        # Return a 400 response if the data was invalid.
        serializer.is_valid(raise_exception=True)

        # Enqueue job
        job = self.celery_job(self.news_factory_class, serializer.data)

        # Create a job serializer
        job_serializer = JobSerializer(
            data={"job_id": job.id},
            context={"request": request},
        )

        # Return the job serializer data
        if job_serializer.is_valid():
            return Response(job_serializer.data)
        else:
            return Response(
                job_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class BaseURLSearchView(BaseJobCreationView):
    """
    Abstract View to create a URL Search Job
    """

    # Define serializer class
    serializer_class = URLSearchSerializer

    @staticmethod
    @shared_task
    def celery_job(factory_cls: NewsFactory, **job_kwargs):
        return factory_cls.from_url_search(**job_kwargs)


class BaseTagSearchView(BaseJobCreationView):
    """
    Abstract View to create a Tag Search Job
    """

    # Define serializer class
    serializer_class = TagSearchSerializer

    @staticmethod
    @shared_task
    def celery_job(factory_cls: NewsFactory, **job_kwargs):
        return factory_cls.from_tag_search(**job_kwargs)


class BaseKeywordSearchView(BaseJobCreationView):
    """
    Abstract View to create a Keyword Search Job
    """

    # Define serializer class
    serializer_class = KeywordSearchSerializer

    @staticmethod
    @shared_task
    def celery_job(factory_cls: NewsFactory, **job_kwargs):
        return factory_cls.from_keyword_search(**job_kwargs)
