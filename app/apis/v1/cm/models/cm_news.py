"""
This module implements the child class 'CMNews' of parent 'News'.
Provides custom logic for CM's news
"""
from __future__ import annotations
from urllib.parse import urlparse
from typing import Union

from lxml import html

from app.core.common.helpers import datetime_from_string, normalize_str

from app.core.common.models.news import News


class CMNews(News):
    @classmethod
    def from_html_string(cls, html_string: str) -> Union[CMNews, None]:

        # Build HTML tree
        tree = html.fromstring(html_string)

        # Extract URL
        url = tree.xpath("//meta[@property='og:url']")[0].get("content")

        # If news is of type 'interativo', 'multimedia' or 'perguntas' skip it
        if any(x in url for x in ["interativo", "multimedia", "perguntas"]):
            return None

        # Get news section from url path and capitalize it
        rubric = urlparse(url).path.split("/")[1].capitalize()
        # Get if news is opinion article from rubric
        is_opinion = rubric == "Opiniao"

        # Find text, author and date location
        author_location = ""
        text_location = ""
        description_location = ""
        date_location = ""
        replace_on_data = ""
        if urlparse(url).netloc == "www.cmjornal.pt":

            author_location = "//span[@class='autor']//text()"
            text_location = "//div[@class='texto_container paywall']//text()[not(ancestor::aside)][not(ancestor::div[@class='inContent'])][not(ancestor::blockquote)]"
            description_location = (
                "//p[@class='destaques_lead']//text()"
                if is_opinion
                else "//strong[@class='lead']//text()"
            )
            date_location = "//span[@class='data']//text()"
            replace_on_data = "às"
        elif urlparse(url).netloc == "www.vidas.pt":

            author_location = "//div[@class='autor']//text()"
            text_location = (
                "//div[@class='text_container']//text()[not(ancestor::iframe)]"
            )
            description_location = "//div[@class='lead']//text()"
            date_location = "//div[@class='data']//text()"
            replace_on_data = "•"

        news_date = datetime_from_string(
            tree.xpath(date_location)[0].replace(replace_on_data, "")
        )

        description = normalize_str(tree.xpath(description_location)[0])
        # Get authors info
        authors = tree.xpath(author_location)
        authors = [normalize_str(a) for a in authors]
        title = tree.xpath("//div[@class='centro']//section//h1")
        # Make sure title exists
        title = title[0].text if len(title) != 0 else ""
        # Normalize title
        title = normalize_str(title)

        text = tree.xpath(text_location)
        # Remove '\n', '\r', and '\'
        text = normalize_str(" ".join(text))
        # Remove ads in case they exist
        text = text.split("Para aceder a todos os Exclusivos CM")[0]
        return cls(
            title,
            description,
            url,
            rubric,
            news_date,
            authors,
            is_opinion,
            text,
        )
