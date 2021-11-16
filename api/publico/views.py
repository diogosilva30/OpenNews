"""
Contains the Publico's API Endpoints (Views)
"""
from core.views import (
    BaseURLSearchView,
    BaseKeywordSearchView,
    BaseTagSearchView,
)

from .models import PublicoNewsFactory


class PublicoURLSearchView(BaseURLSearchView):
    """
    Creates a Publico's URL search job. A
    list of Publico's news URLs must be provided.
    """

    news_factory_class = PublicoNewsFactory


class PublicoTagSearchView(BaseTagSearchView):
    """
    Creates a Publico's Tag search job. A list of tags
    must be provided (e.g. "Política" / "Sociedade" / "Economia" / "Cultura")
    """

    news_factory_class = PublicoNewsFactory


class PublicoKeywordSearchView(BaseKeywordSearchView):
    """
    Creates a Publico's Keyword search job. A list of keywords
    must be provided (e.g. "desporto português")
    """

    news_factory_class = PublicoNewsFactory
