"""
Contains the core news serializers
"""
from rest_framework import serializers
from django.urls import reverse


class BaseDateSearchSerializer(serializers.Serializer):
    """
    Base core serializer for date range related searches
    """

    # Starting search date
    starting_date = serializers.DateField(
        format=None,  # Return date objects
        input_formats=["iso-8601"],
    )

    # Ending search date
    ending_date = serializers.DateField(
        format=None,  # Return date objects
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

        # Check if time delta is equal or less than 3 months (90 days)
        if (attrs["ending_date"] - attrs["starting_date"]).days > 90:
            raise serializers.ValidationError(
                "Please limit your date range to no more than 90 days."
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
        max_length=5,  # Maximum 5 tags
    )


class KeywordSearchSerializer(BaseDateSearchSerializer):
    """
    Core serializer for Keywords Search
    """

    # The list of keywords to search
    keywords = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        max_length=5,  # Maximum 5 Keywords
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
    description = serializers.CharField(allow_blank=True)
    published_at = serializers.DateTimeField()
    url = serializers.URLField()
    rubric = serializers.CharField()
    is_opinion = serializers.BooleanField()
    # Allow blank authors
    authors = serializers.ListField(
        child=serializers.CharField(
            allow_blank=True,
        ),
    )
    text = serializers.CharField()


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
