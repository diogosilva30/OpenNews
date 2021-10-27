"""
Contains tests for CM's URL search
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


# class CMURLSearchAPITest(TestCase):
#     """
#     Performs tests for CM's URL Search
#     """

#     api = APIClient()

#     def test_not_list_payload(self):
#         """
#         Tests creating a URL search job with urls not being a list.
#         Should trigger Bad Request.
#         """
#         response = self.api.post(
#             reverse("cm_url_search"),
#             {
#                 "urls": "https://www.cmjornal.pt/mundo/detalhe/especialista-avisa-que-grandes-casamentos-e-festivais-acabaram-nos-proximos-anos"
#             },
#             format="json",
#         )

#         # Assert 400 response status code
#         self.assertEqual(
#             response.status_code,
#             status.HTTP_400_BAD_REQUEST,
#         )

#         # Assert that error was in `urls`
#         self.assertTrue("urls" in response.data)

#         self.assertEqual(
#             response.data["urls"][0].code,
#             "not_a_list",
#         )

#     def test_invalid_url_format_list_payload(
#         self,
#     ):
#         """
#         Tests creating a URL search job with invalid urls in the url list.
#         """
#         response = self.api.post(
#             reverse("cm_url_search"),
#             {
#                 "urls": [
#                     "https://www.cmjornal.pt/mundo/detalhe/especialista-avisa-que-grandes-casamentos-e-festivais-acabaram-nos-proximos-anos",
#                     "not a valid url",
#                 ]
#             },
#             format="json",
#         )
#         # Assert 400 response status code
#         self.assertEqual(
#             response.status_code,
#             status.HTTP_400_BAD_REQUEST,
#         )

#         # Assert that error was in `urls`
#         self.assertTrue("urls" in response.data)

#         url_errors = list(response.data["urls"].items())[0]

#         # `url_errors` is a tuple containing the indice of invalid url and the error
#         self.assertEqual(url_errors[0], 1)

#         self.assertEqual(url_errors[1][0].code, "invalid")

#     def test_invalid_url(self):
#         """
#         Tests creating jobs with URLs that are not
#         Publico's News
#         """
#         response = self.api.post(
#             reverse("cm_url_search"),
#             {
#                 "urls": [
#                     "https://www.google.pt/",
#                     # Notice that the following link is not a news
#                     "https://www.cmjornal.pt/",
#                 ]
#             },
#             format="json",
#         )
#         # Assert that a `job_id` is returned
#         self.assertIn("job_id", response.data)

#         # Assert that a `results_url` is returned
#         self.assertIn("results_url", response.data)

#         # Make the worker dispatch all jobs in sync mode
#         get_worker().work(burst=True)

#         # Now make the request to get the results
#         response = self.api.get(response.data["results_url"])

#         # Assert that response is status code 200
#         self.assertEqual(
#             response.status_code,
#             status.HTTP_200_OK,
#         )

#     def test_correct_webscraping(self):
#         """
#         Tests if CM URL search jobs are being
#         correctly webscraped.
#         """
#         response = self.api.post(
#             reverse("cm_url_search"),
#             {
#                 # 3 sample news
#                 "urls": [
#                     "https://www.cmjornal.pt/mundo/detalhe/especialista-avisa-que-grandes-casamentos-e-festivais-acabaram-nos-proximos-anos",
#                     "https://www.cmjornal.pt/opiniao/detalhe/palavras-caras",
#                     "https://www.vidas.pt/a-ferver/detalhe/sic-acusa-cristina-ferreira-de-mentir-e-expoe-segredos-da-apresentadora-em-tribunal",
#                 ]
#             },
#             format="json",
#         )

#         # Assert that a `job_id` is returned
#         self.assertIn("job_id", response.data)

#         # Assert that a `results_url` is returned
#         self.assertIn("results_url", response.data)

#         # Make the worker dispatch all jobs in sync mode
#         get_worker().work(burst=True)

#         # Now make the request to get the results
#         response = self.api.get(response.data["results_url"])

#         # Assert that response is status code 200
#         self.assertEqual(
#             response.status_code,
#             status.HTTP_200_OK,
#         )

#         # Number of news should be in response
#         self.assertIn("number_of_news", response.data)
#         # Number of news should be 3
#         self.assertEqual(response.data["number_of_news"], 3)

#         # Get found_news
#         found_news = response.data["news"]

#         # Number of news in the list should be 3 (re-check)
#         self.assertEqual(len(found_news), 3)

#         for news in found_news:
#             # Check if news is well constructed
#             self.assertIn("title", news)
#             self.assertTrue(isinstance(news["title"], str))

#             self.assertIn("description", news)
#             self.assertTrue(isinstance(news["description"], str))

#             self.assertIn("url", news)
#             self.assertTrue(isinstance(news["url"], str))

#             self.assertIn("rubric", news)
#             self.assertTrue(isinstance(news["rubric"], str))

#             self.assertIn("date", news)
#             self.assertTrue(isinstance(news["date"], str))

#             self.assertIn("authors", news)
#             self.assertTrue(isinstance(news["authors"], list))

#             self.assertIn("is_opinion", news)
#             self.assertTrue(isinstance(news["is_opinion"], bool))

#             self.assertIn("text", news)
#             self.assertTrue(isinstance(news["text"], str))

#     def test_unsupported_news_url_search(self):
#         """
#         Tests if CM unsupported news are being skipped.
#         Unsupported types are:
#             -multimedia
#             -interactive
#         """
#         response = self.api.post(
#             reverse("cm_url_search"),
#             {
#                 "urls": [
#                     "https://www.cmjornal.pt/cm-interativo/reportagens-interativas/detalhe/cidade-proibida-china-imperial-secreta-celebra-seis-seculos",
#                     "https://www.cmjornal.pt/multimedia/videos/detalhe/pneumologista-alerta-que-desconfinamento-rapido-pode-aumentar-internamentos-covid-19?ref=Multim%C3%A9dia_DestaquesPrincipais",
#                 ]
#             },
#             format="json",
#         )

#         # Assert that a `job_id` is returned
#         self.assertIn("job_id", response.data)

#         # Assert that a `results_url` is returned
#         self.assertIn("results_url", response.data)

#         # Make the worker dispatch all jobs in sync mode
#         get_worker().work(burst=True)

#         # Now make the request to get the results
#         response = self.api.get(response.data["results_url"])

#         # Assert that response is status code 200
#         self.assertEqual(
#             response.status_code,
#             status.HTTP_200_OK,
#         )

#         # Number of news should be in response
#         self.assertIn("number_of_news", response.data)

#         # Number of news should be 0
#         self.assertEqual(response.data["number_of_news"], 0)
