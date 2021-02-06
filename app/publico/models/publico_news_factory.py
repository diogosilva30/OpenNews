from datetime import datetime
import requests
import os
import json
from urllib.parse import urlparse
import itertools
import pytz


from core.models import NewsFactory
from core.mixins import URLSearchMixin, TagSearchMixin, KeywordSearchMixin
from core.exceptions import UnsupportedNews
from core.utils import datetime_from_string

from .publico_news import PublicoNews


class PublicoNewsFactory(
    URLSearchMixin,
    TagSearchMixin,
    KeywordSearchMixin,
    NewsFactory,
):
    """
    Performs and stores different types of search in Publico's website
    """

    def __init__(self) -> None:
        super().__init__()

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

    def _validate_url(self, url: str) -> bool:
        # First we try to obtain news id from url
        try:
            news_id = urlparse(url).path.split("-")[-1]
        except IndexError:
            return False

        # Check if is integer (try parse)
        try:
            news_id = int(news_id)
        except ValueError:
            return False

        # Make a request with this id and check for valid response (200)
        response = requests.get(
            f"https://api.publico.pt/content/summary/scriptor_noticias/{news_id}"
        )
        if not response.status_code == 200:
            return False
        return super()._validate_url(url)

    def url_search(self, urls: list[str]) -> list[PublicoNews]:
        """
        Iterates over a list of Publico news URLs
        and build Publico News objects.

        Parameters
        ----------
        url: list of str
            List of strings containing Publico's news URLs

        Returns
        -------
        PublicoNews: list
        """
        news_obj_list = []
        for url in urls:
            # If valid URL
            if self._validate_url(url):
                response = self.session.get(url)
                try:
                    news_obj = PublicoNews.from_html_string(response.text)
                    news_obj_list.append(news_obj)
                # Catch unsupported news
                # Continue
                except UnsupportedNews:
                    continue

        return news_obj_list

    def _tag_search(
        self,
        tag: str,
        starting_date: str,
        ending_date: str,
    ) -> list[PublicoNews]:

        # Normalize tag
        tag = tag.replace(" ", "-").lower()
        # Start page number
        page_number = 1
        # Flag to stop the search
        stop_entire_search = False
        # Create news URL list
        collected_news_urls = []

        # Starting date and ending date are timezone unware
        starting_date = pytz.utc.localize(
            datetime_from_string(starting_date, order="YMD"),
        )
        ending_date = pytz.utc.localize(
            datetime_from_string(ending_date, order="YMD"),
        )

        while (
            response := requests.get(
                f"https://www.publico.pt/api/list/{tag}?page={page_number}"
            ).text
        ) != "[]":
            # Read the json data
            data = json.loads(response)
            # iterate over each news dict
            for item in data:
                # Found news out of lower bound date, stop the search
                if datetime_from_string(item.get("data"), order="YMD") < starting_date:
                    stop_entire_search = True  # Will break main loop
                    break  # Will break current loop

                # Found news more recent that end date, SKIP AHEAD
                elif datetime_from_string(item.get("data"), order="YMD") > ending_date:
                    continue

                # Found news inside the date rage, add to list
                else:
                    collected_news_urls.append(item.get("shareUrl"))
            if stop_entire_search:
                break
            # Increment page
            page_number += 1

        return collected_news_urls

    def tag_search(
        self,
        tags: list[str],
        starting_date: str,
        ending_date: str,
    ) -> list[PublicoNews]:
        """
        Performs a tag search of Publico news between the date range,
        merges the news from all tags.

        Parameters
        ----------
        starting_date: str
            The starting search date
        ending_date: str
            The ending search date
        tags: list of str
            The tags to search for
        Returns
        -------
        PublicoNews: list
        """

        # Collect urls from each tag
        news_urls = [self._tag_search(tag, starting_date, ending_date) for tag in tags]

        # `news_urls` is a list of lists. Combine into a single list
        news_urls = list(itertools.chain.from_iterable(news_urls))
        # Remove duplicates
        news_urls = list(dict.fromkeys(news_urls))

        # Perform URL search on each collected url
        return self.url_search(news_urls)

    def _keyword_search(
        self, keyword: str, starting_date: str, ending_date: str
    ) -> list[PublicoNews]:

        # Normalize keyword
        keyword = keyword.lower()
        # Start page number
        page_number = 1
        # Create news URL list
        collected_news_urls = []

        # Starting date and ending date are timezone unware
        starting_date = pytz.utc.localize(
            datetime_from_string(starting_date, order="YMD"),
        )
        ending_date = pytz.utc.localize(
            datetime_from_string(ending_date, order="YMD"),
        )

        while (
            response := requests.get(
                f"https://www.publico.pt/api/list/search/?query={keyword}&start={starting_date.strftime('%d-%m-%Y')}&end={ending_date.strftime('%d-%m-%Y')}&page={page_number}"
            ).text
        ) != "[]":
            # Read the json data
            data = json.loads(response)
            # Get the URLs (this search type needs fullUrl)
            urls = [d.get("fullUrl") for d in data]
            # Append URLs to list
            collected_news_urls += urls
            # Increment page
            page_number += 1

        return collected_news_urls

    def keyword_search(
        self,
        keywords: list[str],
        starting_date: str,
        ending_date: str,
    ) -> list[PublicoNews]:
        """
        Performs a keyword search of Publico news between the date range,
        merges the news from all keywords.

        Parameters
        ----------

        starting_date: str
            The starting search date
        ending_date: str
            The ending search date
        keywords: list of str
            A list of keywords to search for.

        Returns
        -------
        PublicoNews: list
        """
        # Collect urls from each keyword
        news_urls = [
            self._keyword_search(keyword, starting_date, ending_date)
            for keyword in keywords
        ]

        # `news_urls` is a list of lists. Combine into a single list
        news_urls = list(itertools.chain.from_iterable(news_urls))
        # Remove duplicates
        news_urls = list(dict.fromkeys(news_urls))

        # Perform URL search on each collected url
        return self.url_search(news_urls)
