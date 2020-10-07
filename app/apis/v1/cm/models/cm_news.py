from typing import List


from app.core.common.models.news import News
from app.core.common.helpers import (
    datetime_from_string,
    send_post_then_get_html_string,
    validate_url,
)


class CMNews(News):
    def __init__(self, title: str, description: str, url: str, rubric: str, date: str, authors: List[str], is_opinion: bool, text: str):
        super().__init__(title, description, url, rubric, date, authors, is_opinion, text)

    @staticmethod
    def is_news_valid(obj: dict) -> bool:
        pass

    @staticmethod
    def build_from_url(url):
        pass

    @staticmethod
    def deserialize_news(news_dict: dict) -> News:
        pass

    @staticmethod
    def validate_url(url: str) -> bool:
        pass
