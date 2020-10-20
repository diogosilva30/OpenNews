"""
This module defines all the needed classes for storing the
information for all the different CM's searches.
"""
import os
import datetime
import json
from urllib.parse import urlparse
from lxml import html
import requests

from app.core.common.mixins import TagSearchMixin, URLSearchMixin
from app.core.common.helpers import (
    datetime_from_string,
)
from .cm_news import CMNews


class CMSearch(
    TagSearchMixin,
    URLSearchMixin,
):
    """ Class to perform and store different types of search in CM's website"""

    def __init__(self) -> None:
        super(CMSearch).__init__()
        self.found_news = []
        self.session = self._login()

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

    def _url_search(self, url_list: list[str]) -> list[CMNews]:
        """
        Builds 'CMNews' objects from URL list

        Parameters
        ----------
        url: list of str
            CM's news URL list

        Returns
        -------
        list of CMNews
        """

        news_list = [
            CMNews.from_html_string(resp.text)
            for url in url_list
            if (resp := self.session.get(url)).status_code == 200
        ]
        # Remove 'None' values
        return [news for news in news_list if news is not None]

    def _tag_search(
        self, tag: str, start_date: datetime, end_date: datetime
    ) -> list[CMNews]:
        index = 0
        stop_entire_search = False
        # Create news URL list
        collected_news_urls = []
        while True:
            html_string = requests.get(
                f"https://www.cmjornal.pt/mais-sobre/loadmore?contentStartIndex={index}&searchKeywords={tag.replace(' ', '-')}"
            ).text
            if html_string in ["\r\n", ""]:
                break
            tree = html.fromstring(html_string)

            for article in tree.xpath("//article"):

                url = article.xpath(".//h2/a")[0].attrib["data-name"]

                # Make sure URL is correct. Check if it's not a href
                url = (
                    "https://www.cmjornal.pt" + url
                    if urlparse(url).netloc == ""
                    else url
                )

                news_date = datetime_from_string(
                    article.xpath(".//span[@class='dateTime']//a")[0].attrib[
                        "data-dteinit"
                    ]
                )
                if news_date < start_date:
                    stop_entire_search = True
                    break  # stop the local search
                # Found news more recent that end date, SKIP AHEAD
                elif news_date > end_date:
                    continue
                else:
                    collected_news_urls.append(url)

            # Check for full stop
            if stop_entire_search:
                break
            index += 6

        # Webscrappe each collected url
        return self._url_search(collected_news_urls)
