"""
Contains the Publico's API Endpoints (Views)
"""
import django_rq
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .models import PublicoNewsFactory
from core.serializers import (
    TagSearchSerializer,
    JobSerializer,
    URLSearchSerializer,
    KeywordSearchSerializer,
)


class PublicoURLSearchView(APIView):
    """
    Creates a Publico's URL Search job
    """

    def post(self, request, *args, **kwargs):
        # Create serializer from request data
        serializer = URLSearchSerializer(data=request.data)

        if serializer.is_valid():
            # Enqueue job
            job_id = django_rq.enqueue(
                PublicoNewsFactory().url_search,
                urls=serializer.data["urls"],
            ).id

            # Create a job serializer
            job_serializer = JobSerializer(
                data={"job_id": job_id}, context={"request": request}
            )

            # Return the job serializer data
            if job_serializer.is_valid():
                return Response(job_serializer.data)
            else:
                return Response(
                    job_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PublicoTagSearchView(APIView):
    """
    Creates a Publico's Tag Search job
    """

    def post(self, request, *args, **kwargs):
        # Create serializer from request data
        serializer = TagSearchSerializer(data=request.data)
        if serializer.is_valid():
            # Enqueue job
            job_id = django_rq.enqueue(
                PublicoNewsFactory().tag_search,
                starting_date=serializer.data["starting_date"],
                ending_date=serializer.data["ending_date"],
                tags=serializer.data["tags"],
            ).id
            # Create a job serializer
            job_serializer = JobSerializer(
                data={"job_id": job_id},
                context={"request": request},
            )

            # Return the job serializer data
            if job_serializer.is_valid():
                return Response(job_serializer.data)
            else:
                return Response(
                    job_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicoKeywordSearchView(APIView):
    """
    Creates a Publico's Keyword Search job
    """

    def post(self, request, *args, **kwargs):
        # Create serializer from request data
        serializer = KeywordSearchSerializer(data=request.data)
        if serializer.is_valid():
            # Enqueue job
            job_id = django_rq.enqueue(
                PublicoNewsFactory().keyword_search,
                starting_date=serializer.data["starting_date"],
                ending_date=serializer.data["ending_date"],
                keywords=serializer.data["keywords"],
            ).id
            # Create a job serializer
            job_serializer = JobSerializer(
                data={"job_id": job_id},
                context={"request": request},
            )

            # Return the job serializer data
            if job_serializer.is_valid():
                return Response(job_serializer.data)
            else:
                return Response(
                    job_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
