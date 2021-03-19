"""
Contains the CM's API Endpoints (Views)
"""
import django_rq
from rest_framework import generics, mixins, status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from core.serializers import (
    TagSearchSerializer,
    JobSerializer,
    URLSearchSerializer,
    KeywordSearchSerializer,
)

from .models import CMNewsFactory


class CMURLSearchView(
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    """
    Creates a CM's URL Search job
    """

    serializer_class = URLSearchSerializer

    @swagger_auto_schema(responses={201: JobSerializer()})
    def post(self, request, *args, **kwargs):
        # Create serializer from request data
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Enqueue job
            job_id = django_rq.enqueue(
                CMNewsFactory().url_search,
                urls=serializer.data["urls"],
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
                    job_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# class PublicoTagSearchView(APIView):
#     """
#     Creates a Publico's Tag Search job
#     """

#     def post(self, request, *args, **kwargs):
#         # Create serializer from request data
#         serializer = TagSearchSerializer(data=request.data)
#         if serializer.is_valid():
#             # Enqueue job
#             job_id = django_rq.enqueue(
#                 PublicoNewsFactory().tag_search,
#                 starting_date=serializer.data["starting_date"],
#                 ending_date=serializer.data["ending_date"],
#                 tags=serializer.data["tags"],
#             ).id
#             # Create a job serializer
#             job_serializer = JobSerializer(
#                 data={"job_id": job_id},
#                 context={"request": request},
#             )

#             # Return the job serializer data
#             if job_serializer.is_valid():
#                 return Response(job_serializer.data)
#             else:
#                 return Response(
#                     job_serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                 )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PublicoKeywordSearchView(APIView):
#     """
#     Creates a Publico's Keyword Search job
#     """

#     def post(self, request, *args, **kwargs):
#         # Create serializer from request data
#         serializer = KeywordSearchSerializer(data=request.data)
#         if serializer.is_valid():
#             # Enqueue job
#             job_id = django_rq.enqueue(
#                 PublicoNewsFactory().keyword_search,
#                 starting_date=serializer.data["starting_date"],
#                 ending_date=serializer.data["ending_date"],
#                 keywords=serializer.data["keywords"],
#             ).id
#             # Create a job serializer
#             job_serializer = JobSerializer(
#                 data={"job_id": job_id},
#                 context={"request": request},
#             )

#             # Return the job serializer data
#             if job_serializer.is_valid():
#                 return Response(job_serializer.data)
#             else:
#                 return Response(
#                     job_serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                 )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
