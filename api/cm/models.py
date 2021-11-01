"""
Module containg the concrete CMNewsFactory
"""
import requests
import datetime
import os
import json
from lxml import html
from urllib.parse import urlparse

from typeguard import typechecked
from core.utils import datetime_from_string


from core.models import NewsFactory, News
from core.exceptions import UnsupportedNews


@typechecked
class CMNewsFactory(NewsFactory):
    """
    Performs and stores different types of search in CM's website
    """

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

    @staticmethod
    def _parse_cm_news_info(html_tree, is_opinion) -> tuple:
        text = html_tree.xpath(
            "//div[@class='texto_container paywall']//text()[not(ancestor::aside)][not(ancestor::div[@class='inContent'])][not(ancestor::blockquote)]"
        )
        text = " ".join(text)

        if is_opinion:
            description = html_tree.xpath(
                "//p[@class='destaques_lead']//text()"
            )[0]
        else:
            description = html_tree.xpath("//strong[@class='lead']//text()")[0]

        date = html_tree.xpath("//span[@class='data']//text()")[0].replace(
            "às", ""
        )
        authors = html_tree.xpath("//span[@class='autor']//text()")

        return text, description, date, authors

    @staticmethod
    def _parse_vidas_news_info(html_tree, is_opinion):

        text = html_tree.xpath(
            "//div[@class='text_container']//text()[not(ancestor::iframe)]"
        )
        text = " ".join(text)

        description = html_tree.xpath("//div[@class='lead']//text()")[0]
        date = html_tree.xpath("//div[@class='data']//text()")[0].replace(
            "•", ""
        )

        authors = html_tree.xpath("//div[@class='autor']//text()")

        return text, description, date, authors

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
            The built News object

        Raises
        ------
        UnsupportedNews
            If news is one of the following types: "interativo", "multimedia", "perguntas"
        """

        # Build HTML tree
        tree = html.fromstring(html_string)

        # Extract URL
        try:
            url = tree.xpath("//meta[@property='og:url']")[0].get("content")
        except IndexError:
            raise UnsupportedNews

        # If news is of type 'interativo', 'multimedia' or 'perguntas' raise exception
        if any(
            x in url
            for x in [
                "interativo",
                "multimedia",
                "perguntas",
            ]
        ):
            raise UnsupportedNews

        try:
            # Get news section from url path and capitalize it
            rubric = urlparse(url).path.split("/")[1].capitalize()
        except IndexError:
            raise UnsupportedNews

        # Get if news is opinion article from rubric
        is_opinion = rubric == "Opiniao"

        # CM has subjornals with different HTML's (e.g. Vidas - www.vidas.pt)
        # Needs custom webscrapping for each subjornal
        parsed_url_netloc = urlparse(url).netloc
        if parsed_url_netloc == "www.cmjornal.pt":
            parse_func = self._parse_cm_news_info
        elif parsed_url_netloc == "www.vidas.pt":
            parse_func = self._parse_vidas_news_info
        else:
            raise UnsupportedNews(
                f"Unknow news URL netloc: {parsed_url_netloc}"
            )

        # Call the correct method for finding
        # `text`, `description` and `date` elements
        (
            text,
            description,
            published_at,
            authors,
        ) = parse_func(tree, is_opinion)

        # Date must be parsed
        published_at = datetime_from_string(published_at)

        # Remove ads in case they exist
        text = text.split("Para aceder a todos os Exclusivos CM")[0].split(
            "Ler o artigo completo"
        )[0]
        # CM text contains extra white, aswell as carriage
        text = " ".join(text.split())
        # Find title
        title = tree.xpath("//div[@class='centro']//h1//text()")[0]

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

    @classmethod
    def from_keyword_search(
        cls,
        keywords: list[str],
        starting_date: datetime.date,
        ending_date: datetime.date,
    ) -> list[News]:
        """
        Searches news in CM's website by keywords in a date range.
        """
        # Create news URL list
        collected_news_urls = []

        # Format dates
        starting_date = starting_date.strftime("%d/%m/%Y")
        ending_date = ending_date.strftime("%d/%m/%Y")

        # Iterate over the keywords
        for keyword in keywords:
            # Normalize keyword
            keyword = keyword.lower().replace(" ", "-")
            # Start position number
            index = 0

            while (
                response := requests.get(
                    f"https://www.cmjornal.pt/pesquisa/loadmore/?Query={keyword}&FirstPosition={index}&LastPosition={index+9}&Sort=Date&RangeType=Date&FromStr={starting_date}&ToStr={ending_date}&ContentType=All&X-Requested-With=XMLHttpRequest"
                ).text
            ) != "\r\n":

                tree = html.fromstring(response)
                for article in tree.xpath("//article"):
                    url = article.xpath(".//h2/a")[0].attrib["data-name"]
                    # Make sure URL is correct. Check if it's not a href
                    url = (
                        "https://www.cmjornal.pt" + url
                        if url[0] == "/"
                        else url
                    )

                    # Discard url junk
                    url = url.split("?ref")[0]
                    collected_news_urls.append(url)

                # CM returns news in batches of 9
                index += 9

            # Remove (possible) duplicates
            collected_news_urls = list(dict.fromkeys(collected_news_urls))

            # Pass collected URLs to URL Search
            return cls.from_url_search(collected_news_urls)

    @classmethod
    def from_tag_search(
        cls,
        tags: list[str],
        starting_date: datetime.date,
        ending_date: datetime.date,
    ) -> NewsFactory:
        return super().from_tag_search(tags, starting_date, ending_date)
