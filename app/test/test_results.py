import unittest


from app.test.base import BaseTestCase
from .test_publico import send_post_request


class TestResults(BaseTestCase):
    """Performs tests on results resource"""

    def test_non_existing_job(self):
        """ Tests getting results with non existent job_id"""
        response = self.client.get('/api/v1/news/results/1')
        self.assertIn("Job 1 does not exist", response.json["message"])
        self.assert404(response)

    def test_still_processing_job(self):
        """ Tests getting results with still processing job"""
        response = send_post_request(self.client, "/api/v1/news/publico/topic_search", {
            "start_date": "1/3/2020",
            "end_date": "15/3/2020",
            "search_topic": "luanda leaks",
        })
        self.assert200(response)

        # Try to get results
        job_id = response.json["job_id"]
        response = self.client.get(f'/api/v1/news/results/{job_id}')
        self.assertTrue(response.status_code == 202)
        self.assertIn(
            f"Job {job_id} has not been processed yet, try again later", response.json["message"])


if __name__ == "__main__":
    unittest.main()
