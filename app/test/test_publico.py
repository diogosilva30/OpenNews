import unittest


from app.test.base import BaseTestCase
from rq import Queue, Worker
from app.core import redis_queue
workers = Worker.all(queue=redis_queue)


def get_results(client, job_id):
    w = workers[0]
    print(w.name)
    print(w.queues)
    print(w.state)
    print(w.successful_job_count)
    raise ValueError
    i = 0
    while(i < 50):
        response = client.get(f"/api/v1/news/results/{job_id}")
        print(response)
        if response.status_code == 200:
            break
        i = i+1

    return response


class TestPublico(BaseTestCase):
    def test_url_search_job(self):
        """ Test for Publico URL search job creation """
        response = self.client.post("/api/v1/news/publico/",
                                    json={"url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"})
        self.assert200(response)

        response_json = response.json
        self.assertTrue(response_json["status"] == "ok")
        job_id = response_json["job_id"]
        response_json = get_results(self.client, job_id).json
        print(response_json)
        self.assertTrue(int(response_json["number of found news"]) == 1)
        news = response_json["news"][0]
        self.assertTrue(
            news["title"] == "Estudo aponta para resíduos perigosos em novas obras no Parque das Nações", "Correct title missing")
        self.assertTrue(
            "Ou será que vamos viver novamente o drama da CUF Descobertas?" in news["text"], "Full news text missing. Check for Publico's credentials")

    # def test_more_than_50_url_search_job(self):
    #     """ Test for Publico URL search job creation with more than 50 URLS """
    #     response = self.client.post("/api/v1/news/publico/",
    #                                 json={"url": ["https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"]*51})
    #     self.assert400(
    #         response, "URL search with more than 50 URLS should trigger 'Bad Request'")

    # def test_repeated_job_url_search(self):
    #     """ Test for Publico URL search repeated jobs """
    #     response = self.client.post("/api/v1/news/publico/",
    #                                 json={"url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"}).json
    #     previous_job = response["job_id"]
    #     response = self.client.post("/api/v1/news/publico/",
    #                                 json={"url": "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"}).json
    #     new_job = response["job_id"]

    #     self.assertEqual(previous_job, new_job,
    #                      "A request should redirect to a previous matching job")

    # def test_invalid_url_search_job(self):
    #     """ Test for invalid Publico URL search jobs """
    #     response = self.client.post("/api/v1/news/publico/",
    #                                 json={"url": "https://www.pubo.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"})

    #     self.assert400(response)

    # def test_keywords_search_job(self):
    #     """Test for Publico keywords search job"""
    #     response = self.client.post("/api/v1/news/publico/keywords_search/",
    #                                 json={
    #                                     "start_date": "1/1/2020",
    #                                     "end_date": "5/3/2020",
    #                                     "keywords": "covid"
    #                                 })


if __name__ == '__main__':
    unittest.main()
