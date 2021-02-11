"""
Contains tests for Publico's Keyword Search
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django_rq import get_worker
from django.urls import reverse
from rest_framework import status

from core.utils import datetime_from_string


class PublicoKeywordSearchAPITest(TestCase):
    """
    Performs tests for Publico's Keyword Search
    """

    api = APIClient()

    def test_keyword_search_job(self):
        """
        Tests enqueing a Publico's keyword search job and retrieveing news from the job
        """
        start_date = "2020-3-1"
        end_date = "2020-3-15"
        response = self.api.post(
            reverse("publico_keyword_search"),
            {
                "keywords": ["luanda leaks"],
                "starting_date": start_date,
                "ending_date": end_date,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
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
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # Number of news should be in response
        self.assertIn("number_of_news", response.data)

        # Number of news should be 7
        self.assertEqual(response.data["number_of_news"], 7)

        # Get found_news
        found_news = response.data["news"]

        # Number of news in the list should be 7 (re-check)
        self.assertEqual(len(found_news), 7)

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

            # Check that date is inside bound
            self.assertTrue(
                datetime_from_string(start_date, order="YMD").date()
                <= datetime_from_string(news["date"], order="YMD").date()
                <= datetime_from_string(end_date, order="YMD").date(),
                msg="News out of expected date range",
            )
