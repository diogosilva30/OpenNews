from django.test import TestCase
import datetime

from ..models import PublicoNewsFactory


class PublicoFactoryTest(TestCase):
    def test_from_url_search(self):
        """
        Tests if URL search is correctly scrapping news
        """
        factory = PublicoNewsFactory.from_url_search(
            [
                "https://www.publico.pt/2021/01/31/politica/noticia/chega-pede-demissao-conselho-directivo-inem-1948705",
            ]
        )

        # Assert that number of news is 1
        self.assertEqual(len(factory.news), 1)

        # Get the news object
        news_obj = factory.news[0]

        # Check correct fields
        self.assertEqual(
            news_obj.title,
            "Chega pede a demissão do conselho directivo do INEM",
        )

        self.assertEqual(
            news_obj.description,
            """O Iniciativa Liberal exigiu ao primeiro-ministro que assuma “as suas responsabilidades” pelo que chama de “gestão calamitosa do plano de vacinação”.""",
        )

        self.assertEqual(
            news_obj.url,
            "https://www.publico.pt/2021/01/31/politica/noticia/chega-pede-demissao-conselho-directivo-inem-1948705",
        )

        self.assertEqual(
            news_obj.published_at, datetime.datetime(2021, 1, 31, 16, 54, 12)
        )

        self.assertEqual(news_obj.is_opinion, False)

        self.assertEqual(news_obj.rubric, "Política")

        # Authors must be a list
        self.assertEqual(news_obj.authors, ["Luciano Alvarez"])

        # Check the first paragraph of text
        self.assertIn(
            """O Chega pediu, este domingo, a demissão do conselho directivo do INEM, na sequência da aplicação de vacinas contra o covid-19 a cidadãos que não se encontravam nos grupos prioritários.""",
            news_obj.text,
        )

    def test_from_tag_search(self):
        """
        Tests the correct scraping of news by tags
        """
        starting_date = datetime.datetime(2020, 3, 1).date()
        ending_date = datetime.datetime(2020, 3, 15).date()
        factory = PublicoNewsFactory.from_tag_search(
            ["luanda leaks"],
            starting_date=starting_date,
            ending_date=ending_date,
        )

        # Number of news should be greater than 0
        self.assertGreater(len(factory.news), 0)

        for news in factory.news:
            # Check that date is inside bound
            self.assertTrue(
                starting_date <= news.published_at.date() <= ending_date,
                msg="News out of expected date range",
            )

    def test_from_keyword_search(self):
        """
        Tests the correct scraping of news by keywords
        """
        starting_date = datetime.date(2020, 3, 1)
        ending_date = datetime.date(2020, 3, 15)
        factory = PublicoNewsFactory.from_keyword_search(
            ["incêndio", "fogo", "queda", "vento"],
            starting_date=starting_date,
            ending_date=ending_date,
        )

        # Number of news should be > 0
        self.assertGreater(len(factory.news), 0)

        for news in factory.news:
            # Check that date is inside bound
            self.assertTrue(
                starting_date <= news.published_at.date() <= ending_date,
                msg="News out of expected date range",
            )
