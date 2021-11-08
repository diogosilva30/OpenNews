"""
Contains tests for results API
"""
# import datetime
# from django.test import TestCase
# from rest_framework.test import APIClient
# from django.urls import reverse
# from rest_framework import status
# from django_rq import get_worker
# from django.utils.timezone import now

# from core.utils import datetime_from_string


# class ResultsAPITest(TestCase):
#     """
#     Performs tests on Results API
#     """

#     api = APIClient()

#     def test_non_existing_job(self):
#         """
#         Tests the fetching of a non existing job.
#         """
#         response = self.api.get(
#             reverse(
#                 "results",
#                 kwargs={"job_id": "non_existing_job_id"},
#             )
#         )

#         self.assertEqual(
#             response.status_code,
#             status.HTTP_404_NOT_FOUND,
#         )

#     def test_still_processing_job(self):
#         """
#         Tests fetching a job that's still in queue/processing
#         """
#         response = self.api.post(
#             reverse("publico_url_search"),
#             {
#                 "urls": [
#                     "https://www.publico.pt/2021/01/31/economia/noticia/irs-contribuintes-podem-validar-agregado-familiar-ate-15-fevereiro-1948701"
#                 ],
#             },
#         )

#         # Assert that a `job_id` is returned
#         self.assertIn("job_id", response.data)

#         # Assert that a `results_url` is returned
#         self.assertIn("results_url", response.data)

#         # here we dont dispatch the worker so that job stays in queue

#         # Now make the request to get the results
#         response = self.api.get(response.data["results_url"])

#         # Assert that response is status code 200
#         self.assertEqual(
#             response.status_code,
#             status.HTTP_200_OK,
#         )

#     def test_correct_job_response(self):
#         """
#         Tests that the correct elements are returned when
#         fetching job results.
#         """
#         response = self.api.post(
#             reverse("publico_url_search"),
#             {
#                 "urls": [
#                     "https://www.publico.pt/2021/01/31/economia/noticia/irs-contribuintes-podem-validar-agregado-familiar-ate-15-fevereiro-1948701"
#                 ],
#             },
#         )

#         # Assert that a `job_id` is returned
#         self.assertIn("job_id", response.data)

#         # Assert that a `results_url` is returned
#         self.assertIn("results_url", response.data)

#         # here we dispatch the worker so that job gets done in sync mode
#         get_worker().work(burst=True)
#         # Now make the request to get the results
#         response = self.api.get(response.data["results_url"])

#         self.assertIn("number_of_news", response.data)
#         self.assertIn("date", response.data)
#         # Check that date is (almost) equal to now
#         # maximum 1 sec diff
#         self.assertTrue(
#             abs(
#                 now()
#                 - datetime_from_string(
#                     response.data["date"],
#                     order="YMD",
#                 )
#             )
#             < datetime.timedelta(seconds=1)
#         )
#         self.assertIn("news", response.data)
