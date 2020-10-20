"""
This module provides service methods for results endpoint
"""
from flask.json import jsonify
import rq
from rq.job import Job
from app.core.common import custom_exceptions
from worker import conn


def get_results(job_id, connection=conn):
    """
    Checks the status of a job in all the queues

    Parameters
    ----------
    job_id : str
        The id of the job to fetch
    connection : optional
        Redis connection to search jobs
    """

    try:
        fetched_job = Job.fetch(job_id, connection)
    except rq.exceptions.NoSuchJobError as exc:
        raise custom_exceptions.ResourceNotFound(
            f"Job {job_id} does not exist!"
        ) from exc

    if fetched_job.is_finished:
        return jsonify(fetched_job.result)
    elif fetched_job.get_status() == "failed":
        raise custom_exceptions.FailedJob(
            f"Job {job_id} has failed! Stack Trace: {fetched_job.exc_info} "
        )
    else:
        raise custom_exceptions.StillProcessing(
            f"Job {job_id} has not been processed yet, try again later!"
        )
