"""
Module containg the concrete PublicoNewsFactory
"""
import datetime
import requests
import os
import json
from urllib.parse import urlparse
from lxml import html

from django.utils.dateparse import parse_datetime

from typeguard import typechecked

from core.models import NewsFactory, News
from core.exceptions import UnsupportedNews


@typechecked
class PublicoNewsFactory(NewsFactory):
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

    @classmethod
    def from_tag_search(
        cls,
        tags: list[str],
        starting_date: datetime.date,
        ending_date: datetime.date,
    ) -> NewsFactory:
        """
        Searches news in Publico's website by tags, in a date range.
        """

        # Create news URL list
        collected_news_urls = []

        # Iterate over each tag
        for tag in tags:
            # Normalize tag
            tag = tag.replace(" ", "-").lower()
            # Start page number
            page_number = 1
            # Flag to stop the search
            stop_entire_search = False

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
                    if parse_datetime(item.get("data")).date() < starting_date:
                        stop_entire_search = True  # Will break main loop
                        break  # Will break current loop

                    # If news more recent that end date, SKIP AHEAD
                    elif parse_datetime(item.get("data")).date() > ending_date:
                        continue

                    # If news inside the date rage, collect the URL
                    else:

                        collected_news_urls.append(item.get("shareUrl"))
                if stop_entire_search:
                    break
                # Increment page
                page_number += 1

        # Remove (possible) duplicates
        collected_news_urls = list(dict.fromkeys(collected_news_urls))

        # Pass collected URLs to URL Search
        return cls.from_url_search(collected_news_urls)

    @classmethod
    def from_keyword_search(
        cls,
        keywords: list[str],
        starting_date: datetime.date,
        ending_date: datetime.date,
    ) -> NewsFactory:

        # Create news URL list
        collected_news_urls = []

        # Iterate over each keyword
        for keyword in keywords:
            # Normalize keyword
            keyword = keyword.lower()
            # Start page number
            page_number = 1

            while (
                url := f"https://www.publico.pt/api/list/search/?query={keyword}&start={starting_date.strftime('%d-%m-%Y')}&end={ending_date.strftime('%d-%m-%Y')}&page={page_number}"
            ) != "[]":

                print(url)
                # Read the json data
                data = json.loads(requests.get(url).text)

                if not data:
                    break

                # Get the URLs (this search type needs fullUrl)
                urls = [d.get("fullUrl") for d in data]
                # Append URLs to list
                collected_news_urls += urls
                # Increment page
                page_number += 1

        # Remove (possible) duplicates
        collected_news_urls = list(dict.fromkeys(collected_news_urls))

        # Pass collected URLs to URL Search
        return cls.from_url_search(collected_news_urls)

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
        try:
            news_id = int(urlparse(url).path.split("-")[-1])
        except ValueError:
            raise UnsupportedNews(url)

        # Make GET request to publico news summary API endpoint
        response = requests.get(
            f"https://api.publico.pt/content/summary/scriptor_noticias/{news_id}"
        )

        # Load json response
        json_doc = json.loads(response.text)
        # Check if we got any data. If not the news type is not supported
        if json_doc is None:
            raise UnsupportedNews(url)

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
        published_at = parse_datetime(json_doc["data"])

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

        # Remove extra white spaces
        text = " ".join(text.split())

        return News(
            title,
            description,
            url,
            rubric,
            published_at,
            authors,
            is_opinion,
            text,
        )
