from abc import ABC, abstractmethod
from datetime import date
from typing import List
from flask import jsonify

from app.core.common.helpers import date_from_string
from .publico_news import PublicoNews


class PublicoSearch(ABC):
    """Base model to store Publico search news"""
    _found_news: List[PublicoNews]

    @property
    def found_news(self):
        return self._found_news

    @found_news.setter
    def found_news(self, value):
        self._found_news = value

    @property
    def number_of_news(self) -> int:
        return len(self._found_news)

    def __init__(self):
        pass

    @ staticmethod
    def deserialize_search_result(search_results: List[dict]) -> List[PublicoNews]:
        found_news = []
        for item in search_results:
            # Append to array
            found_news.append(PublicoNews.deserialize_news(item))
        return found_news

    @abstractmethod
    def add_news(self, obj: any):
        raise NotImplementedError

    @abstractmethod
    def serialize_to_json(self) -> str:
        raise NotImplementedError


class PublicoTopicSearch(PublicoSearch):
    """Model to store news from Publico's topic search """

    search_topic: str
    start_date: date
    end_date: date

    # __________________________________________________________________________________________________________________________

    def __init__(self, search_topic, start_date, end_date, found_news=[]):
        super().__init__()
        self.search_topic = search_topic
        self.start_date = date_from_string(start_date)
        self.end_date = date_from_string(end_date)
        self.found_news = found_news
    # __________________________________________________________________________________________________________________________

    def serialize_to_json(self) -> str:
        """ Serializes Topic Search object to json"""
        return jsonify({"search topic": self.search_topic,
                        "start date": self.start_date.strftime('%d/%m/%Y'),
                        "end date": self.end_date.strftime('%d/%m/%Y'),
                        "number of found news": str(len(self.found_news)),
                        "news": list(map(lambda x: x.serialize_to_json(), self.found_news))})

    # __________________________________________________________________________________________________________________________

    def add_news(self, data: dict) -> None:
        """Adds a news to the found news list"""
        news_object = PublicoNews.deserialize_news(data)
        # check if object got deserialized, and if news does not already exist
        if isinstance(news_object, PublicoNews) and news_object not in self.found_news:
            self.found_news.append(news_object)


class PublicoURLSearch(PublicoSearch):
    """ Model to store news from Publico's topic search """

    def __init__(self, found_news=[], *args, **kwargs) -> None:
        super(PublicoURLSearch, self).__init__(*args, **kwargs)
        self.found_news = found_news

    def add_news(self, url: str) -> None:
        """Adds a news to the found news list"""
        PublicoNews.validate_url(url)
        news_object = PublicoNews.build_from_url(url)
        if news_object not in self.found_news:
            self.found_news.append(news_object)

    def serialize_to_json(self) -> None:
        """ Serializes URL Search object to json"""
        return jsonify({"number of found news": str(len(self.found_news)),
                        "news": list(map(lambda x: x.serialize_to_json(), self.found_news))})
