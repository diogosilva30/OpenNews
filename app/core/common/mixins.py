from abc import abstractmethod, ABC
from app.core.common.helpers import datetime_from_string


class URLSearchMixin(ABC):
    def url_search(self, url_list: list[str]) -> dict:
        news = self._url_search(url_list)
        return {
            "number of found news": str(len(news)),
            "news": list(map(lambda x: x.to_json(), news)),
        }

    @abstractmethod
    def _url_search(self, url_list: list[str]):
        """ Child classes must implement their own implementation of '_url_search'"""


class TagSearchMixin(ABC):
    def tag_search(self, tag: str, start_date: str, end_date: str) -> dict:
        start_date = datetime_from_string(start_date)
        end_date = datetime_from_string(end_date)
        news = self._tag_search(tag, start_date, end_date)
        return {
            "search tag": tag,
            "start date": start_date.strftime("%d/%m/%Y"),
            "end date": end_date.strftime("%d/%m/%Y"),
            "number of found news": str(len(news)),
            "news": list(map(lambda x: x.to_json(), news)),
        }

    @abstractmethod
    def _tag_search(self, tag: str, start_date: str, end_date: str) -> dict:
        """ Child classes must implement their own implementation of '_tag_search'"""


class KeywordSearchMixin(ABC):
    def keyword_search(self, keyword: str, start_date: str, end_date: str) -> dict:
        start_date = datetime_from_string(start_date)
        end_date = datetime_from_string(end_date)
        news = self._keyword_search(keyword, start_date, end_date)
        return {
            "keyword": keyword,
            "start date": start_date.strftime("%d/%m/%Y"),
            "end date": end_date.strftime("%d/%m/%Y"),
            "number of found news": str(len(news)),
            "news": list(map(lambda x: x.to_json(), news)),
        }
