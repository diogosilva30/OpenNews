from datetime import datetime, timedelta
from rq.job import Job as rqjob


class Job():
    job_id: str
    job_url: str
    expires: datetime

    def __init__(self, job_id, job_url, job_ttl):
        self.job_id = job_id
        self.job_url = job_url
        self.expires = datetime.now() + timedelta(0, job_ttl)

    @staticmethod
    def load(obj: rqjob, url: str):
        return Job(obj.job_id, url, obj.args['result_ttl'])
