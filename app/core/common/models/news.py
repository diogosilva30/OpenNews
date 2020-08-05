import json
from typing import List
from datetime import datetime, date
from abc import ABC, abstractmethod, abstractstaticmethod

from app.core.common.helpers import validate_url, datetime_from_string, custom_json_serializer
from app.core.common.custom_exceptions import RequestError


class News(ABC):
    """ News base model for storing details about a particular news. Derivated classes should implement some methods"""
    title: str
    description: str
    text: str
    url: str
    rubric: str
    date: datetime
    authors: List[str]

    # __________________________________________________________________________________________________________________________

    def __init__(self, title: str, description: str, url: str, rubric: str, date: str, authors: List[str]) -> None:
        self.title = title
        self.description = description

        if(validate_url(url)):
            self.url = url
        else:
            raise RequestError("URL '{}' is not valid!".format(url))
        # Fill in the text variable
        self.extract_corpus()
        self.rubric = rubric
        self.date = datetime_from_string(date)
        self.authors = authors

    # __________________________________________________________________________________________________________________________

    def serialize_to_json(self):
        return json.loads(json.dumps(self, default=custom_json_serializer))

    # __________________________________________________________________________________________________________________________

    @abstractmethod
    def extract_corpus(self) -> None:
        raise NotImplementedError

    # __________________________________________________________________________________________________________________________
    @abstractstaticmethod
    def deserialize_news(news_dict: dict):
        raise NotImplementedError

    # __________________________________________________________________________________________________________________________

    @staticmethod
    def extract_authors_names(authors: List[dict]) -> List[str]:
        """Receives a list of dictionarys containing authors info, and extracts the authors name's to a list"""
        processed_authors = []
        for author in authors:
            # '_authors' is a list of dicts. Keep only the name for each dict
            author = {k: v for k, v in author.items()
                      if k.startswith('nome')}
            # Keep the authors name, unpack them, and add to list
            processed_authors.append(*author.values())
        return processed_authors

    # ___________________________________________________________________________________________________________________________________________________

    @abstractstaticmethod
    def is_news_valid(obj: dict) -> bool:
        """Validates if a particular news is valid given it's dict"""
        raise NotImplementedError

    # _______________________________________________________________________________________________________________________________________________________
    @abstractstaticmethod
    def build_from_url(url) -> 'News':
        """Builds a News object from a given URL"""
        raise NotImplementedError

    @abstractstaticmethod
    def validate_url(url):
        """Validates a URL"""
        raise NotImplementedError

    @abstractstaticmethod
    def parse_date(date_string: str) -> datetime.date:
        """Parses a date string into a date object"""
        raise NotImplementedError
