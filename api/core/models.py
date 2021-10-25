"""
Contains the core news models
"""
from __future__ import annotations
import requests
import json

from abc import (
    ABC,
    abstractmethod,
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

    @property
    def json(self):
        return json.dumps(self.__dict__)


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

    @abstractmethod
    def from_html_string(self, html_string: str) -> News:
        """
        Child factories must implement 'from_html_string' to
        build a news object from a news html page.
        """

    def collect(self, news: News) -> None:
        self.found_news.append(news)

    @property
    def json(self):
        return json.dumps([obj.json for obj in self.found_news])
