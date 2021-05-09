"""
Contains the core news serializers
"""
from rest_framework import serializers
from django.urls import reverse
from django.utils.timezone import now


class BaseDateSearchSerializer(serializers.Serializer):
    """
    Base core serializer for date range related searches
    """

    # Starting search date
    starting_date = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["iso-8601"],
    )

    # Ending search date
    ending_date = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["iso-8601"],
    )

    def validate(self, attrs):
        # Check that `ending_date` is greater than `starting_date`
        if attrs["ending_date"] <= attrs["starting_date"]:
            raise serializers.ValidationError(
                {
                    "ending_date": "The field 'ending_date' must be greater than the field 'starting_date'"
                }
            )
        return super().validate(attrs)


class TagSearchSerializer(BaseDateSearchSerializer):
    """
    Core serializer for Tag Search
    """

    # The list of tags to search
    tags = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )


class KeywordSearchSerializer(BaseDateSearchSerializer):
    """
    Core serializer for Keywords Search
    """

    # The list of keywords to search
    keywords = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )


class URLSearchSerializer(serializers.Serializer):
    """
    Core serializer for URLs search
    """

    # The list of urls to search
    urls = serializers.ListField(
        child=serializers.URLField(),
        allow_empty=False,
    )


class NewsSerializer(serializers.Serializer):
    """
    Core news serializer
    """

    title = serializers.CharField()
    # Allow Blank Descriptions
    description = serializers.CharField(allow_blank = True)
    url = serializers.URLField()
    rubric = serializers.CharField()
    is_opinion = serializers.BooleanField()
    date = serializers.DateTimeField()
    # Allow blank authors
    authors = serializers.ListField(
        child=serializers.CharField(
            allow_blank=True,
        ),
    )
    text = serializers.CharField()


class JobResultSerializer(serializers.Serializer):
    """
    Core job result serializer. Serializes the
    results from a particular job.
    """

    date = serializers.SerializerMethodField()
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

    def to_internal_value(self, data):

        # Create serializer with list of instances
        data = [vars(instance) for instance in data]
        serializer = NewsSerializer(data=data, many=True)
        if serializer.is_valid():
            return {
                "news": serializer.data,
            }

        raise ValueError(serializer.errors)


class JobSerializer(serializers.Serializer):
    """
    Core job serializer
    """

    job_id = serializers.CharField()
    results_url = serializers.SerializerMethodField()

    def get_results_url(self, obj):
        # Get request from context
        request = self.context["request"]
        # Return URL
        return request.build_absolute_uri(
            reverse(
                "results",
                kwargs={"job_id": obj["job_id"]},
            )
        )
