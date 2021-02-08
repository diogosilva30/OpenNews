"""
Contains the CM's News models
"""
from __future__ import annotations

from typing import Union
from lxml import html
from urllib.parse import urlparse

from core.models import News
from core.exceptions import UnsupportedNews


class CMNews(News):
    """
    CM's news model
    """

    @staticmethod
    def _parse_cm_news_info(html_tree, is_opinion):
        text = html_tree.xpath(
            "//div[@class='texto_container paywall']//text()[not(ancestor::aside)][not(ancestor::div[@class='inContent'])][not(ancestor::blockquote)]"
        )
        text = " ".join(text)

        if is_opinion:
            description = html_tree.xpath("//p[@class='destaques_lead']//text()")[0]
        else:
            description = html_tree.xpath("//strong[@class='lead']//text()")[0]

        date = html_tree.xpath("//span[@class='data']//text()")[0].replace("às", "")
        authors = html_tree.xpath("//span[@class='autor']//text()")

        return text, description, date, authors

    @staticmethod
    def _parse_vidas_news_info(html_tree, is_opinion):

        text = html_tree.xpath(
            "//div[@class='text_container']//text()[not(ancestor::iframe)]"
        )
        text = " ".join(text)

        description = html_tree.xpath("//div[@class='lead']//text()")[0]
        date = html_tree.xpath("//div[@class='data']//text()")[0].replace("•", "")
        authors = html_tree.xpath("//div[@class='autor']//text()")

        return text, description, date, authors

    @classmethod
    def from_html_string(cls, html_string: str) -> Union[CMNews]:
        """
        Builds a News object from a given URL.

        Parameters
        ----------
        html_string : str
            A news page HTML's string

        Returns
        -------
        CMNews
            The built CMNews object

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
        if any(x in url for x in ["interativo", "multimedia", "perguntas"]):
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
            parse_func = CMNews._parse_cm_news_info
        elif parsed_url_netloc == "www.vidas.pt":
            parse_func = CMNews._parse_vidas_news_info
        else:
            raise UnsupportedNews(f"Unknow news URL netloc: {parsed_url_netloc}")

        # Call the correct method for finding
        # `text`, `description` and `date` elements
        (
            text,
            description,
            date,
            authors,
        ) = parse_func(tree, is_opinion)

        # Remove ads in case they exist
        text = text.split("Para aceder a todos os Exclusivos CM")[0].split(
            "Ler o artigo completo"
        )[0]
        text = text.replace("\\n", "").replace("\\r", "")
        # Find title
        title = tree.xpath("//div[@class='centro']//h1//text()")[0]

        return cls(
            title,
            description,
            url,
            rubric,
            date,
            authors,
            is_opinion,
            text,
        )
