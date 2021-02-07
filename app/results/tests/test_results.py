"""
Contains tests for results API
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


class ResultsAPITest(TestCase):
    """
    Performs tests on Results API
    """

    api = APIClient()

    def test_non_existing_job(self):
        """
        Tests the fetching of a non existing job.
        """
        response = self.api.get(
            reverse("results", kwargs={"job_id": "non_existing_job_id"})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_still_processing_job(self):
        """
        Tests fetching a job that's still in queue/processing
        """
        response = self.api.post(
            reverse("publico_url_search"),
            {
                "urls": [
                    "https://www.publico.pt/2021/01/31/economia/noticia/irs-contribuintes-podem-validar-agregado-familiar-ate-15-fevereiro-1948701"
                ],
            },
        )

        # Assert that a `job_id` is returned
        self.assertIn("job_id", response.data)

        # Assert that a `results_url` is returned
        self.assertIn("results_url", response.data)

        # here we dont dispatch the worker so that job stays in queue

        # Now make the request to get the results
        response = self.api.get(response.data["results_url"])

        # Assert that response is status code 202
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
