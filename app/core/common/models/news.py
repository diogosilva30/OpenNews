"""
This module implements the base news class 'News'.
This class stores information about a particular news
"""
from __future__ import annotations

import json
from abc import ABC, abstractclassmethod
from typing import Union


from app.core.common.helpers import datetime_from_string, custom_json_serializer


class News(ABC):
    """ News base model for storing details about a particular news. Derivated classes should implement some methods"""

    def __init__(
        self,
        title: str,
        description: str,
        url: str,
        rubric: str,
        date: str,
        authors: list[str],
        is_opinion: bool,
        text: str,
    ) -> None:
        self.title = title
        self.description = description
        self.url = url
        self.rubric = rubric
        self.is_opinion = is_opinion
        self.date = datetime_from_string(date)
        self.authors = authors
        self.text = text

    def to_json(self):
        """ Serializes a 'News' object to JSON """
        return json.loads(json.dumps(self, default=custom_json_serializer))

    def __repr__(self) -> str:
        return json.dumps(self.to_json())

    @abstractclassmethod
    def from_html_string(cls, html_string: str) -> Union[News, None]:
        """ Child classes must implement 'from_html_string' to build a news object from a news html page"""
