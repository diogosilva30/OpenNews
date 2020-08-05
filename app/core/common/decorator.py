import os
from functools import wraps
import jwt
from flask import request, jsonify, url_for

from worker import conn

from rq.job import Job
import app.core.common.custom_exceptions as custom_exceptions
from app.core import redis_queue


def prevent_duplicate_jobs(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # Extract passed json args into function
        function_args = request.get_json()

        # Get list of completed jobs in redis queue
        completed_job_ids = redis_queue.finished_job_registry.get_job_ids()

        # Fetch for jobs with the previously obtained id's
        jobs = Job.fetch_many(completed_job_ids, conn)
        # Check for existence of finished job with same passed args
        for job in jobs:
            if function_args in job.args:
                print(
                    "Detected a request for already existing finished job '{}'! Redirecting...".format(job.get_id()))
                return jsonify({'job_id': job.get_id(), 'Results URL': url_for(
                    'api_v1.results', job_id=str(job.get_id()), _external=True)})

        # If not found in finished jobs, check queued jobs
        # Gets a list of enqueued job instances
        queued_jobs = redis_queue.jobs
        # Iterate over queued_jobs
        for queued_job in queued_jobs:
            if function_args in queued_job.args:
                print(
                    "Detected a request for already queued existing job '{}'! Redirecting...".format(queued_job.get_id()))
                return jsonify({'job_id': queued_job.get_id(), 'Results URL': url_for(
                    'api_v1.results', job_id=str(queued_job.get_id()), _external=True)})

        # Get list of currently executing jobs in redis queue
        current_jobs_ids = redis_queue.started_job_registry.get_job_ids()

        # Fetch for jobs with the previously obtained id's
        jobs = Job.fetch_many(current_jobs_ids, conn)
        # Check for existence of executing job with same passed args
        for job in jobs:
            if function_args in job.args:
                print(
                    "Detected a request for already executing job '{}'! Redirecting...".format(job.get_id()))
                return jsonify({'job_id': job.get_id(), 'Results URL': url_for(
                    'api_v1.results', job_id=str(job.get_id()), _external=True)})

        return f(*args, **kwargs)
    return decorated
