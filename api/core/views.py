"""
Core views
"""
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
    """
    Base abstract view to create search jobs via POST method.
    """

    # Child views must define a news Factory class
    news_factory_class: NewsFactory = None

    # Child views must define the factory method that should be called
    news_factory_method: str = None

    # Child views must define a serializer class
    serializer_class = None

    @staticmethod
    @shared_task
    def celery_job(
        news_factory_class: NewsFactory,
        news_factory_method: str,
        **data,
    ):
        """
        Child classes must implement this static method to create
        a celery job.
        """
        # First get the factory instance
        factory = news_factory_class()

        # Now get the factory method that should be called
        factory_method = getattr(factory, news_factory_method)

        # Call the method with the data
        return factory_method(**data)

    @swagger_auto_schema(responses={201: JobSerializer()})
    def post(self, request, *args, **kwargs):
        # Create serializer from request data
        serializer = self.get_serializer(data=request.data)

        # Check for request errors
        # Return a 400 response if the data was invalid.
        serializer.is_valid(raise_exception=True)

        # Enqueue job
        job = self.celery_job.delay(
            self.news_factory_class,
            self.news_factory_method,
            **serializer.data,  # unpack dict data to factory method
        )

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

    # Define the factory method to be called
    news_factory_method = "from_url_search"


class BaseTagSearchView(BaseJobCreationView):
    """
    Abstract View to create a Tag Search Job
    """

    # Define serializer class
    serializer_class = TagSearchSerializer

    # Define the factory method to be called
    news_factory_method = "from_tag_search"


class BaseKeywordSearchView(BaseJobCreationView):
    """
    Abstract View to create a Keyword Search Job
    """

    # Define serializer class
    serializer_class = KeywordSearchSerializer

    # Define the factory method to be called
    news_factory_method = "from_keyword_search"
