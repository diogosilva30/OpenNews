import datetime
from django.test import TestCase
from ..models import CMNewsFactory


class CMFactoryTest(TestCase):
    def test_from_url_search(self):
        """
        Tests if URL search is correctly scrapping news
        """
        factory = CMNewsFactory.from_url_search(
            [
                "https://www.cmjornal.pt/mundo/detalhe/especialista-avisa-que-grandes-casamentos-e-festivais-acabaram-nos-proximos-anos",
            ]
        )

        # Assert that number of news is 1
        self.assertEqual(len(factory.news), 1)

        # Get the news object
        news_obj = factory.news[0]

        # Check correct fields
        self.assertEqual(
            news_obj.title,
            "Especialista avisa que grandes casamentos e festivais são para esquecer nos 'próximos anos'",
        )

        self.assertEqual(
            news_obj.description,
            """Professor em epidemiologia genética do King's College London, no Reino Unido, afirmou que grandes eventos não vão acontecer como "antigamente".""",
        )

        self.assertEqual(
            news_obj.url,
            "https://www.cmjornal.pt/mundo/detalhe/especialista-avisa-que-grandes-casamentos-e-festivais-acabaram-nos-proximos-anos",
        )

        self.assertEqual(
            news_obj.published_at, datetime.datetime(2021, 2, 7, 15, 19)
        )

        self.assertEqual(news_obj.is_opinion, False)

        self.assertEqual(news_obj.rubric, "Mundo")

        # Authors must be a list
        self.assertEqual(news_obj.authors, ["Correio da Manhã"])

        # Check the first paragraph of text
        self.assertIn(
            """Um professor em epidemiologia genética do King's College London, no Reino Unido, afirmou que grandes eventos como casamentos não vão acontecer como "antigamente" durante os próximos anos devido à ameaça que representa o coronavírus.""",
            news_obj.text,
        )

    def test_from_keyword_search(self):
        """
        Tests the correct scraping of news by keywords
        """
        starting_date = datetime.datetime(2020, 3, 1).date()
        ending_date = datetime.datetime(2020, 3, 15).date()
        factory = CMNewsFactory.from_keyword_search(
            ["Luanda leaks"],
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

    def test_from_tag_search(self):
        """
        Tests the correct scraping of news by tags
        """
        today = datetime.datetime.now()

        ending_date = (today - datetime.timedelta(days=5)).date()
        starting_date = (today - datetime.timedelta(days=20)).date()

        factory = CMNewsFactory.from_tag_search(
            ["Economia"],
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
