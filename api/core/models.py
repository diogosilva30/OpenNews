"""
Contains the core news models
"""
from __future__ import annotations
import datetime
import requests
import json

from typeguard import typechecked


from abc import (
    ABC,
    abstractclassmethod,
    abstractmethod,
    abstractstaticmethod,
)

from .exceptions import UnsupportedNews


@typechecked
class News(ABC):
    """
    Abstract news base model for storing details about a particular news. Derivated classes should implement some methods.

    Type hints are hard checked, and a error is raised if type does not match the type hint.

    * Abstract class
    """

    def __init__(
        self,
        title: str,
        description: str,
        url: str,
        rubric: str,
        published_at: datetime.datetime,
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
        published_at: datetime
            The news published datetime
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
        self.published_at = published_at
        self.authors = authors
        self.text = text

    @property
    def json(self) -> str:
        return json.dumps(self.__dict__)


@typechecked
class NewsFactory(ABC):
    """
    Abstract news factory.

    Type hints are hard checked, and a error is raised if type does not match the type hint.

    """

    def __init__(self) -> None:
        # Empty list for storing found news
        self.news = []
        self.session = self._login()

    @abstractstaticmethod
    def _login() -> requests.Session:
        """
        Concrete factories must provide their own implementation
        of this method to perform login on a particular news website,
        and return the login session.
        """

    @classmethod
    def from_url_search(cls, urls: list[str]) -> NewsFactory:
        """
        Instanciates a news factory, and build the news list from
        a list of URLs.

        Parameters
        ----------
        urls: list of str
            List of strings containing news URLs

        Returns
        -------
        NewsFactory
        """
        instance = cls()
        for url in urls:
            # If valid URL
            if instance._validate_url(url):
                response = instance.session.get(url)
                try:
                    news_obj = instance.from_html_string(response.text)
                    instance.news.append(news_obj)
                # Catch unsupported news
                # Continue
                except UnsupportedNews:
                    continue

        return instance

    @abstractclassmethod
    def from_tag_search(
        cls,
        tags: list[str],
        starting_date: datetime.date,
        ending_date: datetime.date,
    ) -> NewsFactory:
        """
        Abstract class method that child classes must implement
        to instantiate a factory with news collected from a tag search.
        """

    @abstractclassmethod
    def from_keyword_search(
        cls,
        keywords: list[str],
        starting_date: datetime.date,
        ending_date: datetime.date,
    ) -> NewsFactory:
        """
        Abstract class method that child classes must implement
        to instantiate a factory with news collected from a keyword search.
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
        build a `News` object from a news html page.
        """

    @property
    def json(self):
        return json.dumps([obj.json for obj in self.news])
