import unittest

from flask import json

from app.apis.v1.publico.services.publico_news_service import search_by_keywords, search_by_topic, search_by_urls
from app.test.base import BaseTestCase, get_results_from_fake_queue, fake_redis_queue


# class TestPublicoURLSearch(BaseTestCase):

#     def _enqueue_url_search_job(self, data: dict, number_of_news: int = 1):
#         # Enqueue fake job with data
#         search_job = fake_redis_queue.enqueue(
#             search_by_urls, data)

#         # Assert that the job is finished
#         self.assertTrue(search_job.is_finished)

#         # Get json response from the job
#         response_json = get_results_from_fake_queue(search_job.id).json

#         # Assert that 'number of found news' exists and is only 1
#         self.assertEqual(
#             str(response_json["number of found news"]), str(number_of_news), "Incorrect number of news")

#         # Check for correct information and premium text in news
#         news = response_json["news"][0]
#         self.assertTrue(
#             news["title"] == "Estudo aponta para resíduos perigosos em novas obras no Parque das Nações", "Correct title missing")

#         # fake_redis_queue.delete(delete_jobs=True)

#     def test_url_search_job(self):
#         """ Test for Publico URL fake job creation and news retrieval"""
#         data = {"url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"}
#         self._enqueue_url_search_job(data)

#     def test_repeated_urls_search_job(self):
#         """ Test for Publico URL fake job creation with 5 repeated URLS. Should only retrieve one"""
#         # Create 5 repeated urls
#         data = {"url": [
#             "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"]*5}
#         self._enqueue_url_search_job(data)

#     def test_more_than_50_url_search_job(self):
#         """ Test for Publico URL search job creation with more than 50 URLS """
#         data = {"url": [
#             "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"]*51}

#         # Validation should be at resource endpoint. Send POST request to the API
#         response = self.client.post('/api/v1/news/publico/', json=data)

#         self.assertEqual(response.json["status"], "error")
#         self.assertIn("Too many URLS to search", response.json["message"])
#         self.assert400(
#             response, "URL search with more than 50 URLS should trigger 'Bad Request'")

#     def test_repeated_job_url_search(self):
#         """ Test for Publico URL search repeated jobs. A subsequent job request should redirect to a previous equal existing job """
#         response = self.client.post("/api/v1/news/publico/",
#                                     json={"url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"}).json
#         previous_job = response["job_id"]
#         response = self.client.post("/api/v1/news/publico/",
#                                     json={"url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"}).json
#         new_job = response["job_id"]

#         self.assertEqual(previous_job, new_job,
#                          "A request should redirect to a previous matching job")

#     def test_invalid_url_search_job(self):
#         """ Test for invalid Publico URL search jobs """
#         response = self.client.post("/api/v1/news/publico/",
#                                     json={"url": "https://www.pubo.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"})

#         self.assert400(response)


class TestPublicoKeywordsSearch(BaseTestCase):
    def _enqueue_keywords_search_job(self, data: dict, number_of_news: int = 1):
        pass

    def test_keywords_search_job(self):
        """ Test for Publico Keywords fake job creation and news retrieval"""
        # Create 5 repeated urls
        data = {
            "start_date": "1/6/2020",
            "end_date": "5/6/2020",
            "keywords": "covid"
        }
        self._enqueue_keywords_search_job(data)

        # Enqueue fake job with data
        search_job = fake_redis_queue.enqueue(
            search_by_keywords, data)

        # Assert that the job is finished
        self.assertTrue(search_job.is_finished)

        # Get json response from the job
        response_json = get_results_from_fake_queue(search_job.id).json

        self.assertIn("number of found news", response_json)


if __name__ == '__main__':
    unittest.main()
