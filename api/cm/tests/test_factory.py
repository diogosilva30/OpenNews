import datetime
from django.test import TestCase
from ..models import CMNewsFactory


class CMURLSearchAPITest(TestCase):
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
