"""
Contains the CM's API Endpoints (Views)
"""

from core.views import (
    BaseURLSearchView,
    BaseKeywordSearchView,
    BaseTagSearchView,
)

from .models import CMNewsFactory


class CMURLSearchView(BaseURLSearchView):
    """
    Define the custom CM URL Search job creation view.
    We only need to define the concrete news factory.
    """

    news_factory_class = CMNewsFactory


class CMTagSearchView(BaseTagSearchView):
    """
    Define the custom CM Tag Search job creation view.
    We only need to define the concrete news factory.
    """

    news_factory_class = CMNewsFactory


class CMKeywordSearchView(BaseKeywordSearchView):
    """
    Define the custom CM Keyword Search job creation view.
    We only need to define the concrete news factory.
    """

    news_factory_class = CMNewsFactory
