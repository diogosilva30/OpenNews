import unittest

from app.apis.v1.cm.services.cm_news_service import (
    search_by_topic
)
from app.tests.base import BaseTestCase, get_results_from_fake_queue, fake_redis_queue


def send_post_request(client, uri, json_payload):
    """ Helper method to send POST request to the API"""
    # Send post
    return client.post(uri, json=json_payload)


class TestCMTopicSearch(BaseTestCase):
    """ Performs tests for Publico's Topic Search"""

    # URI for this resource
    uri = "/api/v1/news/cm/topic_search"

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
        self._enqueue_topic_search_job({
            "start_date": "1/3/2020",
            "end_date": "15/3/2020",
            "search_topic": "luanda leaks",
        })

    def test_invalid_dates_topic_search_job(self):
        """ Test for CM topic search with invalid date format """
        response = send_post_request(self.client, self.uri, {
            "start_date": "not a valid date",
            "end_date": "another invalid date",
            "keywords": "covid",
        })

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Invalid date string format provided",
                      response.json["message"])

        self.assert400(
            response, "Keyword search should trigger 'Bad Request'! Dates are invalid"
        )

    def test_starting_date_older_than_ending_date(self):
        """ Test for Publico topic search with starting date > ending date """
        response = send_post_request(self.client, self.uri, {
            "start_date": "5/03/2020",
            "end_date": "10/3/2019",
            "keywords": "covid",
        })

        self.assertEqual(response.json["status"], "error")
        self.assertIn("Invalid dates provided", response.json["message"])

        self.assert400(
            response,
            "Keyword search should trigger 'Bad Request'! Dates are invalid (starting date > ending date)",
        )


if __name__ == "__main__":
    unittest.main()
