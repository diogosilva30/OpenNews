from rq.job import Job as rqjob
import app.core.common.custom_exceptions as custom_exceptions
from worker import conn


def get_results(job_id, connection=conn):
    try:
        fetched_job = rqjob.fetch(job_id, connection)

    except:
        raise custom_exceptions.ResourceNotFound(
            "Job {} does not exist!".format(job_id)
        )

    if fetched_job.is_finished:
        return fetched_job.result.serialize_to_json()
    elif fetched_job.get_status() == "failed":
        raise custom_exceptions.FailedJob(
            "Job {} has failed!".format(job_id), fetched_job.exc_info
        )
    else:
        raise custom_exceptions.StillProcessing(
            "Job {} has not been processed yet, try again later!".format(job_id)
        )
