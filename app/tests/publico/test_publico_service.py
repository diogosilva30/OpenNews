import unittest


from app.apis.v1.publico.services.publico_news_service import (
    search_by_keywords,
    search_by_topic,
    search_by_urls,
)
from app.tests.base import BaseTestCase, get_results_from_fake_queue, fake_redis_queue


def send_post_request(client, uri, json_payload):
    """ Helper method to send POST request to the API"""
    # Send post
    return client.post(uri, json=json_payload)


class TestPublicoURLSearch(BaseTestCase):
    """ Performs tests for Publico's URL search"""

    uri = "/api/v1/news/publico/"

    def _enqueue_url_search_job(self, data: dict):
        # Enqueue fake job with data
        search_job = fake_redis_queue.enqueue(search_by_urls, data)

        # Assert that the job is finished
        self.assertTrue(search_job.is_finished)

        # Get json response from the job
        response_json = get_results_from_fake_queue(search_job.id).json

        self.assertIn("number of found news", response_json)
        self.assertIn("title", response_json["news"][0])
        self.assertIn("description", response_json["news"][0])
        self.assertIn("text", response_json["news"][0])
        self.assertIn("url", response_json["news"][0])
        self.assertIn("rubric", response_json["news"][0])
        self.assertIn("date", response_json["news"][0])
        self.assertIn("authors", response_json["news"][0])
        self.assertIn("is_opinion", response_json["news"][0])

    def test_url_search_job(self):
        """ Test for Publico URL fake job creation and news retrieval"""

        self._enqueue_url_search_job(
            {
                "url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
            }
        )

    def test_repeated_urls_search_job(self):
        """ Test for Publico URL fake job creation with 5 repeated URLS. Should only retrieve one"""
        # Create 5 repeated urls
        self._enqueue_url_search_job(
            {
                "url": [
                    "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
                ]
                * 5
            }
        )

    def test_invalid_urls_search_job(self):
        """ Test for Publico URL fake job creation with invalid URLs. Should raise RequestError"""
        # Send 3 invalid urls (1 not url, 1 bad url, 1 unsupported URL (ipsilon))
        response = send_post_request(
            self.client,
            self.uri,
            {
                "url": [
                    "notavalidurl",
                    "www.goggle.pt",
                    "https://www.publico.pt/2020/10/01/culturaipsilon/noticia/artistas-exigem-publico-possa-ja-pinturas-ku-klux-klan-philip-guston-1933604",
                ]
            },
        )
        self.assert400(
            response,
            "Publico'sURL search job with invalid URLs should raise RequestError and return 400 status code",
        )

    def test_more_than_50_url_search_job(self):
        """ Test for Publico URL search job creation with more than 50 URLS """

        # Validation should be at resource endpoint. Send POST request to the API
        response = send_post_request(
            self.client,
            self.uri,
            {
                "url": [
                    "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
                ]
                * 51
            },
        )

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Too many URLS to search", response.json["message"])
        self.assert400(
            response, "URL search with more than 50 URLS should trigger 'Bad Request'"
        )

    def test_previous_existing_url_search_job(self):
        """ Test for Publico URL search repeated jobs. A subsequent job request should redirect to a previous equal existing job """
        response = send_post_request(
            self.client,
            self.uri,
            {
                "url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
            },
        ).json

        previous_job = response["job_id"]
        response = send_post_request(
            self.client,
            self.uri,
            {
                "url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
            },
        ).json

        new_job = response["job_id"]

        self.assertEqual(
            previous_job,
            new_job,
            "A request should redirect to a previous matching job",
        )

    def test_invalid_url_search_job(self):
        """ Test for invalid Publico URL search jobs """
        response = send_post_request(
            self.client,
            self.uri,
            {
                "url": "https://www.pubo.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
            },
        )

        self.assert400(response)


class TestPublicoKeywordsSearch(BaseTestCase):
    """ Performs tests for Publico's keywords search"""

    uri = "/api/v1/news/publico/keywords_search"

    def _enqueue_keywords_search_job(self, data: dict):
        # Enqueue fake job with data
        search_job = fake_redis_queue.enqueue(search_by_keywords, data)

        # Assert that the job is finished
        self.assertTrue(search_job.is_finished)

        # Get json response from the job
        response_json = get_results_from_fake_queue(search_job.id).json

        self.assertIn("number of found news", response_json)

    def test_keywords_search_job(self):
        """ Test for Publico Keywords fake job creation and news retrieval"""
        # Create 5 repeated urls
        data = {"start_date": "4/6/2020", "end_date": "5/6/2020", "keywords": "covid"}
        self._enqueue_keywords_search_job(data)

    def test_previous_existing_keywords_search_job(self):
        """ Test for Publico keywords search repeated jobs. A subsequent job request should redirect to a previous equal existing job """

        response = send_post_request(
            self.client,
            self.uri,
            {"start_date": "4/6/2020", "end_date": "5/6/2020", "keywords": "covid"},
        ).json
        previous_job = response["job_id"]
        response = send_post_request(
            self.client,
            self.uri,
            {"start_date": "4/6/2020", "end_date": "5/6/2020", "keywords": "covid"},
        ).json

        new_job = response["job_id"]
        self.assertEqual(
            previous_job,
            new_job,
            "A request should redirect to a previous matching job",
        )

    def test_invalid_date_range_keywords_search_job(self):
        """ Test for Publico keywords search with invalid date range (greater than 3 months) """
        response = send_post_request(
            self.client,
            self.uri,
            {"start_date": "4/2/2020", "end_date": "5/6/2020", "keywords": "covid"},
        )

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Date range is too big", response.json["message"])

        self.assert400(
            response,
            "Keyword search should trigger 'Bad Request'! Date range is too big",
        )

    def test_invalid_dates_keywords_search_job(self):
        """ Test for Publico keywords search with invalid date format """
        response = send_post_request(
            self.client,
            self.uri,
            {
                "start_date": "not a valid date",
                "end_date": "another invalid date",
                "keywords": "covid",
            },
        )

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Invalid date string format provided", response.json["message"])

        self.assert400(
            response, "Keyword search should trigger 'Bad Request'! Dates are invalid"
        )

    def test_starting_date_older_than_ending_date(self):
        """ Test for Publico keyword search with starting date > ending date """
        response = send_post_request(
            self.client,
            self.uri,
            {"start_date": "5/03/2020", "end_date": "10/3/2019", "keywords": "covid"},
        )

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Invalid dates provided", response.json["message"])

        self.assert400(
            response,
            "Keyword search should trigger 'Bad Request'! Dates are invalid (starting date > ending date)",
        )


class TestPublicoTopicSearch(BaseTestCase):
    """ Performs tests for Publico's Topic Search"""

    # URI for this resource
    uri = "/api/v1/news/publico/topic_search"

    def _enqueue_topic_search_job(self, data: dict):
        """ Enqueues job for topic_search on the fake redis server"""

        # Enqueue fake job with data
        search_job = fake_redis_queue.enqueue(search_by_topic, data)

        # Assert that the job is finished
        self.assertTrue(search_job.is_finished)

        # Get json response from the job
        response_json = get_results_from_fake_queue(search_job.id).json

        # Check that news were found
        self.assertIn("number of found news", response_json)

    def test_topic_search_job(self):
        """ Test for Publico topic fake job creation and news retrieval"""
        self._enqueue_topic_search_job(
            {
                "start_date": "1/3/2020",
                "end_date": "15/3/2020",
                "search_topic": "luanda leaks",
            }
        )

    def test_invalid_dates_topic_search_job(self):
        """ Test for Publico topic search with invalid date format """
        response = send_post_request(
            self.client,
            self.uri,
            {
                "start_date": "not a valid date",
                "end_date": "another invalid date",
                "keywords": "covid",
            },
        )

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Invalid date string format provided", response.json["message"])

        self.assert400(
            response, "Keyword search should trigger 'Bad Request'! Dates are invalid"
        )

    def test_starting_date_older_than_ending_date(self):
        """ Test for Publico topic search with starting date > ending date """
        response = send_post_request(
            self.client,
            self.uri,
            {"start_date": "5/03/2020", "end_date": "10/3/2019", "keywords": "covid"},
        )

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Invalid dates provided", response.json["message"])

        self.assert400(
            response,
            "Keyword search should trigger 'Bad Request'! Dates are invalid (starting date > ending date)",
        )


if __name__ == "__main__":
    unittest.main()
