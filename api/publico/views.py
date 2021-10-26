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
    Define the custom Publico URL Search job creation view.
    We only need to define the concrete news factory.
    """

    news_factory_class = PublicoNewsFactory


class PublicoTagSearchView(BaseTagSearchView):
    """
    Define the custom Publico Tag Search job creation view.
    We only need to define the concrete news factory.
    """

    news_factory_class = PublicoNewsFactory


class PublicoKeywordSearchView(BaseKeywordSearchView):
    """
    Define the custom Publico Keyword Search job creation view.
    We only need to define the concrete news factory.
    """

    news_factory_class = PublicoNewsFactory
