"""
Contains the core mixins that concrete news factorys should inherit to implement
a functionality
"""
from abc import ABC, abstractmethod, abstractclassmethod

from .models import News


class URLSearchMixin(ABC):
    """
    Mixin class for concrete news factorys that implement URL Search
    """

    @abstractclassmethod
    def from_url_search(cls, url_list: list[str]) -> list[News]:
        """
        Abstract method that child classes must implement
        to provide their own logic for URL Search.
        """


class TagSearchMixin(ABC):
    """
    Mixin class for concrete news factorys that implement Tag Search
    """

    @abstractclassmethod
    def from_tag_search(
        cls,
        tags: list[str],
        starting_date: str,
        ending_date: str,
    ) -> list[News]:
        """
        Abstract method that child classes must implement
        to provide their own logic for Tag Search.
        """


class KeywordSearchMixin(ABC):
    """
    Mixin class for concrete news factorys that implement Keyword Search
    """

    @abstractclassmethod
    def from_keyword_search(
        cls,
        keywords: list[str],
        starting_date: str,
        ending_date: str,
    ) -> list[News]:
        """
        Abstract method that child classes must implement
        to provide their own logic for Keyword Search.
        """
