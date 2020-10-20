"""
This module defines all the needed classes for storing the
information for all the different Publico's searches.
"""
import os
import json
from datetime import datetime

import requests

from app.core.common.mixins import KeywordSearchMixin, TagSearchMixin, URLSearchMixin
from app.core.common.helpers import datetime_from_string
from .publico_news import PublicoNews


class PublicoSearch(
    URLSearchMixin,
    KeywordSearchMixin,
    TagSearchMixin,
):
    """ Class to perform and store different types of search in Publico's website"""

    def __init__(self) -> None:
        self.found_news = []
        self.session = self._login()

    @staticmethod
    def _login() -> requests.Session:
        """
        Creates a 'requests.Session', performs login on Publico's Website and returns the session
        """

        login_payload = {
            "username": os.getenv("PUBLICO_USER"),
            "password": os.getenv("PUBLICO_PW"),
        }
        login_url = "https://www.publico.pt/api/user/login"
        session = requests.Session()
        session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
            }
        )
        # send POST request to login
        session.post(login_url, data=login_payload)
        return session

    def _url_search(self, url_list: list[str]) -> PublicoNews:
        """
        Builds 'PublicoNews' object from URL

        Parameters
        ----------
        url: str
            Publico's news URL

        Returns
        -------
        PublicoNews
        """
        news_list = [
            PublicoNews.from_html_string(resp.text)
            for url in url_list
            if (resp := self.session.get(url)).status_code == 200
        ]

        return [news for news in news_list if news is not None]

    def _tag_search(self, tag: str, start_date: datetime, end_date: datetime):
        # Flag to stop search
        stop_entire_search = False
        # Normalize tag
        tag = tag.replace(" ", "-").lower()
        # Start page number
        page_number = 1
        # Create news URL list
        collected_news_urls = []
        # Start the reading loop
        while (
            response := requests.get(
                f"https://www.publico.pt/api/list/{tag}?page={page_number}"
            ).text
        ) != "[]":
            # Read the json data
            data = json.loads(response)
            # iterate over each news dict and create a News object from it
            for item in data:
                # Found news out of lower bound date, STOP THE SEARCH!

                if datetime_from_string(item.get("data"), order="YMD") < start_date:
                    stop_entire_search = True
                    break  # stop the local search
                # Found news more recent that end date, SKIP AHEAD
                elif datetime_from_string(item.get("data"), order="YMD") > end_date:
                    continue
                # Found news inside the date rage, add to list
                else:
                    collected_news_urls.append(item.get("shareUrl"))
            if stop_entire_search:
                break
            # Increment page
            page_number += 1

        # Webscrappe each collected url
        return self._url_search(collected_news_urls)

    def _keyword_search(
        self,
        keyword: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[PublicoNews]:
        # Normalize keyword
        keyword = keyword.lower()
        # Start page number
        page_number = 1
        # Create news URL list
        collected_news_urls = []

        while (
            response := requests.get(
                f"https://www.publico.pt/api/list/search/?query={keyword}&start={start_date.strftime('%d-%m-%Y')}&end={end_date.strftime('%d-%m-%Y')}&page={page_number}"
            ).text
        ) != "[]":
            # Read the json data
            data = json.loads(response)
            # Get the URLs
            urls = [d.get("shareUrl") for d in data]
            # Append URLs to list
            collected_news_urls += urls
            # Increment page
            page_number += 1

        # Webscrappe each collected url
        return self._url_search(collected_news_urls)
