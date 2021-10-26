"""
Module containg the concrete PublicoNewsFactory
"""
import requests
import os
import json
from urllib.parse import urlparse
import itertools
from lxml import html


from core.models import NewsFactory, News
from core.mixins import (
    URLSearchMixin,
    TagSearchMixin,
    KeywordSearchMixin,
)
from core.exceptions import UnsupportedNews
from core.utils import datetime_from_string


class PublicoNewsFactory(
    URLSearchMixin,
    TagSearchMixin,
    KeywordSearchMixin,
    NewsFactory,
):
    """
    Performs and stores different types of search in Publico's website
    """

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

    def url_search(self, urls: list[str]) -> list[News]:
        """
        Iterates over a list of Publico news URLs
        and build Publico News objects.

        Parameters
        ----------
        url: list of str
            List of strings containing Publico's news URLs

        Returns
        -------
        News: list
        """
        news_obj_list = []
        for url in urls:
            # If valid URL
            if self._validate_url(url):
                response = self.session.get(url)
                try:
                    news_obj = self.from_html_string(response.text)
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
    ) -> list[News]:

        # Normalize tag
        tag = tag.replace(" ", "-").lower()
        # Start page number
        page_number = 1
        # Flag to stop the search
        stop_entire_search = False
        # Create news URL list
        collected_news_urls = []

        # Parse `starting_date`
        starting_date = datetime_from_string(starting_date, order="YMD").date()
        # Parse `ending_date`
        ending_date = datetime_from_string(ending_date, order="YMD").date()

        while (
            response := requests.get(
                f"https://www.publico.pt/api/list/{tag}?page={page_number}"
            ).text
        ) != "[]":
            # Read the json data
            data = json.loads(response)
            # iterate over each news dict
            for item in data:
                # If news out of lower bound date, stop the search
                if (
                    datetime_from_string(
                        item.get("data"),
                        order="YMD",
                    ).date()
                    < starting_date
                ):
                    stop_entire_search = True  # Will break main loop
                    break  # Will break current loop

                # If news more recent that end date, SKIP AHEAD
                elif (
                    datetime_from_string(
                        item.get("data"),
                        order="YMD",
                    ).date()
                    > ending_date
                ):
                    continue

                # If news inside the date rage, collect the URL
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
    ) -> list[News]:
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
        news_urls = [
            self._tag_search(tag, starting_date, ending_date) for tag in tags
        ]

        # `news_urls` is a list of lists. Combine into a single list
        news_urls = list(itertools.chain.from_iterable(news_urls))
        # Remove duplicates
        news_urls = list(dict.fromkeys(news_urls))

        # Perform URL search on each collected url
        return self.url_search(news_urls)

    def _keyword_search(
        self,
        keyword: str,
        starting_date: str,
        ending_date: str,
    ) -> list[News]:

        # Normalize keyword
        keyword = keyword.lower()
        # Start page number
        page_number = 1
        # Create news URL list
        collected_news_urls = []

        # Parse `starting_date`
        starting_date = datetime_from_string(starting_date, order="YMD")
        # Parse `ending_date`
        ending_date = datetime_from_string(ending_date, order="YMD")

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
    ) -> list[News]:
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
        News: list
        """
        # Collect urls from each keyword
        news_urls = [
            self._keyword_search(
                keyword,
                starting_date,
                ending_date,
            )
            for keyword in keywords
        ]

        # `news_urls` is a list of lists. Combine into a single list
        news_urls = list(itertools.chain.from_iterable(news_urls))
        # Remove duplicates
        news_urls = list(dict.fromkeys(news_urls))

        # Perform URL search on each collected url
        return self.url_search(news_urls)

    def from_html_string(self, html_string: str) -> News:
        """
        Builds a News object from a given URL.

        Parameters
        ----------
        html_string : str
            A news page HTML's string

        Returns
        -------
        News
            The built News object.

        Raises
        ------
        UnsupportedNews
            If news is minute updated.
        """

        # Build HTML tree
        tree = html.fromstring(html_string)

        # Extract URL
        url = tree.xpath("//meta[@property='og:url']")[0].get("content")

        # Extract news id
        news_id = urlparse(url).path.split("-")[-1]

        # Make GET request to publico news summary API endpoint
        response = requests.get(
            f"https://api.publico.pt/content/summary/scriptor_noticias/{news_id}"
        )
        # Load json response
        json_doc = json.loads(response.text)

        # Delete every key that has 'None' value
        json_doc = {k: v for k, v in json_doc.items() if v is not None}

        # If minute updated news, raise Unsupported News
        minuteUpdated = tree.xpath("//span[@class='label label--live']")

        if len(minuteUpdated) != 0:
            raise UnsupportedNews

        # Extract description, might be null.
        # Therefore use a empty string as default
        description = json_doc.get("descricao", "")
        # Extract if news is opinion
        is_opinion = json_doc["isOpiniao"]
        # Extract news title
        title = json_doc["titulo"]
        # Get authors list
        authors = [author.get("nome") for author in json_doc["autores"]]
        # Get rubric
        rubric = json_doc["seccao"]
        # Get news date, already is in ISO 8601 format
        date = json_doc["data"]

        # Extract text
        text = " ".join(
            tree.xpath(
                (
                    "//div[@class='story__body']//p//text()[not(ancestor::aside)][not(ancestor::div[contains(@class, 'supplemental-slot')])] | \
                //div[@class='story__body']//blockquote//text()[not(ancestor::aside)][not(ancestor::div[contains(@class, 'supplemental-slot')])]  | \
                //div[@class='story__body']//*[self::h1 or self::h2 or self::h3 or self::h4]//text()[not(ancestor::aside)][not(ancestor::div[contains(@class, 'supplemental-slot')])]"
                )
            )
        ).replace(
            "Subscreva gratuitamente as newsletters e receba o melhor da actualidade e os trabalhos mais profundos do Público.",
            "",
        )

        return News(
            title,
            description,
            url,
            rubric,
            date,
            authors,
            is_opinion,
            text,
        )
