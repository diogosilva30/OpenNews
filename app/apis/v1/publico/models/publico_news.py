import os
from lxml import html
import requests
from datetime import date
from dateutil import parser
from app.core.common.models.news import News
from app.core.common.helpers import datetime_from_string, send_post_then_get_html_string, validate_url
from app.core.common.custom_exceptions import RequestError


class PublicoNews(News):

    def __init__(self, title, description, url, rubric, date, authors):
        super().__init__(title, description, url, rubric, date, authors)

    def extract_corpus(self) -> None:
        # GET request to read the html page
        html_string = send_post_then_get_html_string("https://www.publico.pt/api/user/login", {"username": os.getenv('PUBLICO_USER'),
                                                                                               "password": os.getenv('PUBLICO_PW')}, self.url)
        # Load html page into a tree
        tree = html.fromstring(html_string)
        # Find the news text by XPATH, and remove in text ads
        self.text = ' '.join(tree.xpath(
            "//div[@class='story__body']//p//text() | //div[@class='story__body']//h2//text()")) \
            .replace("Subscreva gratuitamente as newsletters e receba o melhor da actualidade e os trabalhos mais profundos do Público.", "")

    # _______________________________________________________________________________________________________________________________________________________

    @staticmethod
    def is_news_valid(obj: dict) -> bool:
        """Validates if a particular news is valid given it's dict"""
        # Check for 'interviews', and 'right to answer'

        # Validate URL
        if not validate_url(obj.get("url")):
            return False

        rubric = str(obj.get("rubrica"))
        if "Entrevista" in rubric or "Direito de Resposta" in rubric:
            return False

        # Skip minute updated news
        if bool(obj.get("aoMinuto")) is True:
            return False

        # Skip Opinion articles
        if bool(obj.get("isOpinion")) is True:
            return False

        news_type = str(obj.get("tipo"))
        if "NOTICIA" not in news_type:
            return False

        return True

    # _______________________________________________________________________________________________________________________________________________________

    @classmethod
    def build_from_url(cls, url):
        """Builds a News object from a given URL"""
        html_string = send_post_then_get_html_string("https://www.publico.pt/api/user/login", {"username": os.getenv('PUBLICO_USER'),
                                                                                               "password": os.getenv('PUBLICO_PW')}, url)
        tree = html.fromstring(html_string)

        _url = url

        _title = tree.xpath(
            '//*[@id="story-header"]/h1//text()')[0].replace('\\n', '').replace('\n', '')

        if "opiniao" in url:
            rubric_element = tree.xpath(
                '//*[@id="story-header"]/div[2]//text()')
            _rubric = ''.join(rubric_element)

            # get description
            description_element = tree.xpath(
                '//*[@id="story-header"]/div[3]/p/text()')
            _description = ''.join([s for s in description_element if s !=
                                    "\n" and s != " " and s != 't'])
            authors_element = tree.xpath(
                '//*[@id="story-header"]/div[1]/address/a/span[2]/text()')
            _authors = [s for s in authors_element if s !=
                        "\n" and s != " " and s != "\t"]

        else:
            rubric_element = tree.xpath(
                '//*[@id="story-header"]/div[1]/a//text()')
            _rubric = ''.join(rubric_element)

            description_element = tree.xpath(
                '//*[@id="story-header"]/div[2]//text()')
            _description = ''.join(
                [s for s in description_element if s != "\n" and s != " " and s != "\t"])

            authors_element = tree.xpath(
                '//*[@id="story-header"]/div[3]/div[1]/div//text()')
            _authors = [s for s in authors_element if s !=
                        "\n" and s != " " and s != "\t" and s != ' e ']

        date_element = ''.join(tree.xpath(
            '//time[contains(@class, "dateline")]')[0].xpath('@datetime'))
        _date = datetime_from_string(date_element)

        return PublicoNews(_title, _description, _url, _rubric, _date, _authors)

    # _______________________________________________________________________________________________________________________________________________________

    @staticmethod
    def deserialize_news(news_dict: dict) -> 'News':
        """Converts a dictionary (containing a particular news information) to a News object"""
        # Check is news is valid, if not return None. If it's valid proced to deserialize
        if not PublicoNews.is_news_valid(news_dict):
            return None

        # Extract title
        _title = news_dict.get("titulo")
        # Extract description
        _description = " " if news_dict.get(
            "descricao") is None else news_dict.get("descricao")
        # Extract URL
        _url = news_dict.get("shareUrl")
        # Extract rubric
        _rubric = news_dict.get("rubrica")
        # Extract date
        _date = news_dict.get("data")
        # Extract authors info
        _authors = PublicoNews.extract_authors_names(news_dict.get("autores"))
        return PublicoNews(_title, _description, _url, _rubric, _date, _authors)

    # TODO: Add support for more "subjornals" from Publico
    @staticmethod
    def validate_url(url):
        try:
            if (requests.get(url).status_code == 200 and "www.publico.pt" in url and ("noticia" in url or "opiniao" in url) and "ipsilon" not in url):
                return True
            else:
                raise RequestError(
                    "URL '{}' is invalid or unsupported!".format(url))
        except:
            raise RequestError(
                "URL '{}' is invalid or unsupported!".format(url))

    @staticmethod
    def parse_date(date_string: str) -> date:
        return parser.parse(date_string).date()
