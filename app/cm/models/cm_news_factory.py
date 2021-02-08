"""
Module containg the concrete CMNewsFactory
"""
import requests
import os
import json

from core.mixins import (
    URLSearchMixin,
    TagSearchMixin,
    KeywordSearchMixin,
)
from core.models import NewsFactory
from core.exceptions import UnsupportedNews

from .cm_news import CMNews


class CMNewsFactory(
    URLSearchMixin,
    NewsFactory,
):
    """
    Performs and stores different types of search in CM's website
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _login() -> requests.Session:
        """
        Creates a 'requests.Session', performs login on CM's Website and returns the session
        """

        # Create session
        session = requests.Session()

        payload = {
            "email": os.getenv("CM_USER", ""),
            "password": os.getenv("CM_PW", ""),
        }

        # Send POST request
        resp = session.post(
            "https://aminhaconta.xl.pt/Async/Site/LoginHandler/LOGIN_WITH_THIRDPARTY",
            data=payload,
        )
        json_response = json.loads(resp.text)
        if not json_response["Success"]:
            token = ""
        else:
            token = json.loads(resp.text)["Data"]["LOGIN_TOKEN"]

        session.get(
            f"https://www.cmjornal.pt/login/login?token={token}&returnUrl=https://www.cmjornal.pt"
        )

        return session

    def url_search(self, urls: list[str]) -> list[CMNews]:
        """
        Iterates over a list of CM news URLs
        and build CM News objects.

        Parameters
        ----------
        url: list of str
            List of strings containing CM's news URLs

        Returns
        -------
        CMNews: list
        """
        news_obj_list = []
        for url in urls:
            # If valid URL
            if self._validate_url(url):
                response = self.session.get(url)
                try:
                    news_obj = CMNews.from_html_string(response.text)
                    news_obj_list.append(news_obj)
                # Catch unsupported news
                # Continue
                except UnsupportedNews:
                    continue

        return news_obj_list
