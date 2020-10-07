import json
import os
from typing import List
from datetime import datetime
from abc import ABC, abstractstaticmethod

from lxml import html

from app.core.common.helpers import datetime_from_string, custom_json_serializer, send_post_then_get_html_string


class News(ABC):
    """ News base model for storing details about a particular news. Derivated classes should implement some methods"""

    def __init__(
        self,
        title: str,
        description: str,
        url: str,
        rubric: str,
        date: str,
        authors: List[str],
        is_opinion: bool,
        text: str
    ) -> None:
        self.title = title
        self.description = description
        self.url = url
        self.rubric = rubric
        self.is_opinion = is_opinion
        self.date = datetime_from_string(date)
        self.authors = authors
        self.text = text

    def serialize_to_json(self):
        return json.loads(json.dumps(self, default=custom_json_serializer))

    @abstractstaticmethod
    def deserialize_news(news_dict: dict):
        """Child classes must implement method 'deserialize_news' to construct a 'News' object from a dictionary"""

    @staticmethod
    def extract_authors_names(authors: List[dict]) -> List[str]:
        """Receives a list of dictionarys containing authors info, and extracts the authors name's to a list"""
        processed_authors = []
        for author in authors:
            # '_authors' is a list of dicts. Keep only the name for each dict
            author = {k: v for k, v in author.items() if k.startswith("nome")}
            # Keep the authors name, unpack them, and add to list
            processed_authors.append(*author.values())
        return processed_authors

    @abstractstaticmethod
    def is_news_valid(obj: dict) -> bool:
        """Child classes must implement 'is_news_valid' to check if a particular news is valid given it's dict"""

    @abstractstaticmethod
    def build_from_url(url) -> "News":
        """Child classes must implement 'build_from_url' method to build a 'News' object from a given URL"""

    @abstractstaticmethod
    def validate_url(url):
        """Child classes must implement 'validate_url' method check if a URL is valid"""

    @abstractstaticmethod
    def parse_date(date_string: str) -> datetime.date:
        """Child classes must implement 'parse_date' method to parse a date string into a date object"""
