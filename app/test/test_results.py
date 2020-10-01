import unittest


from app.test.base import BaseTestCase


class TestResults(BaseTestCase):
    """Performs tests on results resource"""

    def test_non_existing_job(self):
        response = self.client.get('/api/news/results/1')
        self.assertIn("Job 1 does not exist", response.json["message"])
        self.assert404(response)
