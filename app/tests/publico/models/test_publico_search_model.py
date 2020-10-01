
import unittest
from app.tests.base import BaseTestCase
from app.apis.v1.publico.models.publico_search import PublicoURLSearch


class TestPublicoSearchModel(BaseTestCase):
    """ Performs tests on Publico search models"""

    def test_building_opinion_article_from_url(self):
        """ Tests adding opinion article to URL search"""
        results = PublicoURLSearch()
        results.add_news(
            "https://www.publico.pt/2020/10/01/opiniao/opiniao/biden-velho-amigo-china-1933470")


if __name__ == "__main__":
    unittest.main()
