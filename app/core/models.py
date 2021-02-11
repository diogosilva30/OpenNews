"""
Contains the core news models
"""
from __future__ import annotations
from typing import Union
import requests

from abc import (
    ABC,
    abstractclassmethod,
    abstractstaticmethod,
)


class News(ABC):
    """
    Abstract news base model for storing details about a particular news. Derivated classes should implement some methods

    * Abstract class
    """

    def __init__(
        self,
        title: str,
        description: str,
        url: str,
        rubric: str,
        date: str,
        authors: list[str],
        is_opinion: bool,
        text: str,
    ) -> None:
        """
        Base constructor for a News object.

        Parameters
        ----------
        title: str
            The news title
        description: str
            The news description
        url: str
            The news URL
        rubric: str
            The news rubric
        date: str
            The news date in ISO 8601 format
        authors: list of str
            A list of the news authors
        is_opinion: bool
            If the news is opinion article or not
        text: str
            The news body.
        """
        self.title = title
        self.description = description
        self.url = url
        self.rubric = rubric
        self.is_opinion = is_opinion
        self.date = date
        self.authors = authors
        self.text = text

    @abstractclassmethod
    def from_html_string(cls, html_string: str) -> Union[News]:
        """
        Child classes must implement 'from_html_string' to build a news object from a news html page.
        Might return `None` is that news is not supported.
        """


class NewsFactory(ABC):
    """
    Abstract news factory
    """

    def __init__(self) -> None:
        # Empty list for storing found news
        self.found_news = []
        self.session = self._login()

    @abstractstaticmethod
    def _login() -> requests.Session:
        """
        Concrete factories must provide their own implementation
        of this method to perform login on a particular news website,
        and return the login session.
        """

    def _validate_url(self, url: str) -> bool:
        """
        Validates than a given URL returns a 200 status code
        """
        return self.session.get(url).status_code == 200
