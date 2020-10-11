from rq.job import Job as rqjob
import app.core.common.custom_exceptions as custom_exceptions
from worker import conn


def get_results(job_id, connection=conn):
    try:
        fetched_job = rqjob.fetch(job_id, connection)

    except:
        raise custom_exceptions.ResourceNotFound(
            f"Job {job_id} does not exist!"
        )

    if fetched_job.is_finished:
        return fetched_job.result.serialize_to_json()
    elif fetched_job.get_status() == "failed":
        raise custom_exceptions.FailedJob(
            f"Job {job_id} has failed! Stack Trace: {fetched_job.exc_info} "
        )
    else:
        raise custom_exceptions.StillProcessing(
            f"Job {job_id} has not been processed yet, try again later!"
        )
