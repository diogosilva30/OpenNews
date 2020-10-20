"""
This module implements the child class 'PublicoNews' of parent 'News'.
Provides custom logic for Publico's news
"""
from __future__ import annotations
import json
from typing import Union
from urllib.parse import urlparse
import requests
from lxml import html

from app.core.common.models.news import News


class PublicoNews(News):
    @classmethod
    def from_html_string(cls, html_string: str) -> Union[PublicoNews, None]:
        """Builds a News object from a given URL.
        Returns None if:
            - News is minute-updated.

        Parameters
        ----------
        html_string : str
            A news page HTML's string

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

        # If minute updated news, return none
        if json_doc["aoMinuto"]:
            return None
        # Extract info
        description = json_doc["descricao"]
        is_opinion = json_doc["isOpinion"]
        title = json_doc["titulo"]
        authors = [author.get("nome") for author in json_doc["autores"]]
        rubric = json_doc["seccao"]
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

        return cls(title, description, url, rubric, date, authors, is_opinion, text)
