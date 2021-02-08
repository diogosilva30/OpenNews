"""
Contains tests for Publico's URL search
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django_rq import get_worker
from django.urls import reverse
from rest_framework import status


class PublicoURLSearchAPITest(TestCase):
    """
    Performs tests for Publico's URL Search
    """

    api = APIClient()

    def test_not_list_payload(self):
        """
        Tests creating a URL search job with urls not being a list.
        Should trigger Bad Request.
        """
        response = self.api.post(
            reverse("publico_url_search"),
            {
                "urls": "https://www.publico.pt/2021/01/30/sociedade/noticia/covid19-comissao-governo-comissao-dgs-desacordo-vacinacao-1948605"
            },
            format="json",
        )

        # Assert 400 response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that error was in `urls`
        self.assertTrue("urls" in response.data)

        self.assertEqual(response.data["urls"][0].code, "not_a_list")

    def test_invalid_url_format_list_payload(self):
        """
        Tests creating a URL search job with invalid urls in the url list.
        """
        response = self.api.post(
            reverse("publico_url_search"),
            {
                "urls": [
                    "https://www.publico.pt/2021/01/30/sociedade/noticia/covid19-comissao-governo-comissao-dgs-desacordo-vacinacao-1948605",
                    "not a valid url",
                ]
            },
            format="json",
        )
        # Assert 400 response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that error was in `urls`
        self.assertTrue("urls" in response.data)

        url_errors = list(response.data["urls"].items())[0]

        # `url_errors` is a tuple containing the indice of invalid url and the error
        self.assertEqual(url_errors[0], 1)

        self.assertEqual(url_errors[1][0].code, "invalid")

    def test_invalid_url(self):
        """
        Tests creating jobs with URLs that are not
        Publico's News
        """
        response = self.api.post(
            reverse("publico_url_search"),
            {
                "urls": [
                    "https://www.google.pt/",
                    # Notice the typo 'xxxx'
                    "https://www.publico.pt/2021/01/31/economia/noticia/irs-contribuintes-podem-validar-agregado-familiar-ate-15-fevereiro-xxxx",
                    # not a news
                    "https://www.publico.pt/",
                ]
            },
            format="json",
        )
        # Assert that a `job_id` is returned
        self.assertIn("job_id", response.data)

        # Assert that a `results_url` is returned
        self.assertIn("results_url", response.data)

        # Make the worker dispatch all jobs in sync mode
        get_worker().work(burst=True)

        # Now make the request to get the results
        response = self.api.get(response.data["results_url"])

        # Assert that response is status code 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Number of news should be in response
        self.assertIn("number_of_news", response.data)

        # Number of news should be 0
        self.assertEqual(response.data["number_of_news"], 0)

    def test_correct_webscraping(self):
        """
        Tests if Publico URL search jobs are being
        correctly webscraped.
        """
        response = self.api.post(
            reverse("publico_url_search"),
            {
                # 2 sample news
                "urls": [
                    "https://www.publico.pt/2021/01/31/politica/noticia/chega-pede-demissao-conselho-directivo-inem-1948705",
                    "https://www.publico.pt/2021/01/31/economia/noticia/irs-contribuintes-podem-validar-agregado-familiar-ate-15-fevereiro-1948701",
                ]
            },
            format="json",
        )

        # Assert that a `job_id` is returned
        self.assertIn("job_id", response.data)

        # Assert that a `results_url` is returned
        self.assertIn("results_url", response.data)

        # Make the worker dispatch all jobs in sync mode
        get_worker().work(burst=True)

        # Now make the request to get the results
        response = self.api.get(response.data["results_url"])

        # Assert that response is status code 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Number of news should be in response
        self.assertIn("number_of_news", response.data)

        # Number of news should be 2
        self.assertEqual(response.data["number_of_news"], 2)

        # Get found_news
        found_news = response.data["news"]

        # Number of news in the list should be 2 (re-check)
        self.assertEqual(len(found_news), 2)

        for news in found_news:
            # Check if news is well constructed
            self.assertIn("title", news)
            self.assertTrue(isinstance(news["title"], str))

            self.assertIn("description", news)
            self.assertTrue(isinstance(news["description"], str))

            self.assertIn("url", news)
            self.assertTrue(isinstance(news["url"], str))

            self.assertIn("rubric", news)
            self.assertTrue(isinstance(news["rubric"], str))

            self.assertIn("date", news)
            self.assertTrue(isinstance(news["date"], str))

            self.assertIn("authors", news)
            self.assertTrue(isinstance(news["authors"], list))

            self.assertIn("is_opinion", news)
            self.assertTrue(isinstance(news["is_opinion"], bool))

            self.assertIn("text", news)
            self.assertTrue(isinstance(news["text"], str))

    def test_minute_update_url_search(self):
        """
        Tests if Publico minute updated news are being skipped.
        Minute updated news are not supported.
        """
        response = self.api.post(
            reverse("publico_url_search"),
            {
                "urls": [
                    "https://www.publico.pt/2021/01/30/sociedade/noticia/covid19-comissao-governo-comissao-dgs-desacordo-vacinacao-1948605",
                ]
            },
            format="json",
        )

        # Assert that a `job_id` is returned
        self.assertIn("job_id", response.data)

        # Assert that a `results_url` is returned
        self.assertIn("results_url", response.data)

        # Make the worker dispatch all jobs in sync mode
        get_worker().work(burst=True)

        # Now make the request to get the results
        response = self.api.get(response.data["results_url"])

        # Assert that response is status code 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Number of news should be in response
        self.assertIn("number_of_news", response.data)

        # Number of news should be 0
        self.assertEqual(response.data["number_of_news"], 0)
