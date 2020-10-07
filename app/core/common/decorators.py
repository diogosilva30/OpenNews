from functools import wraps
from flask import request, jsonify, url_for
from rq.job import Job

from worker import conn

from app.core.common.custom_exceptions import RequestError
from app.core.common.helpers import datetime_from_string, number_of_months_between_2_dates
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
                    "Detected a request for already existing finished job '{}'! Redirecting...".format(
                        job.get_id()
                    )
                )
                return jsonify(
                    {
                        "status": "ok",
                        "job_id": job.get_id(),
                        "Results URL": url_for(
                            "api_v1.results", job_id=str(job.get_id()), _external=True
                        ),
                    }
                )

        # If not found in finished jobs, check queued jobs
        # Gets a list of enqueued job instances
        queued_jobs = redis_queue.jobs
        # Iterate over queued_jobs
        for queued_job in queued_jobs:
            if function_args in queued_job.args:
                print(
                    "Detected a request for already queued existing job '{}'! Redirecting...".format(
                        queued_job.get_id()
                    )
                )
                return jsonify(
                    {
                        "status": "ok",
                        "job_id": queued_job.get_id(),
                        "Results URL": url_for(
                            "api_v1.results",
                            job_id=str(queued_job.get_id()),
                            _external=True,
                        ),
                    }
                )

        # Get list of currently executing jobs in redis queue
        current_jobs_ids = redis_queue.started_job_registry.get_job_ids()

        # Fetch for jobs with the previously obtained id's
        jobs = Job.fetch_many(current_jobs_ids, conn)
        # Check for existence of executing job with same passed args
        for job in jobs:
            if function_args in job.args:
                print(
                    "Detected a request for already executing job '{}'! Redirecting...".format(
                        job.get_id()
                    )
                )
                return jsonify(
                    {
                        "status": "ok",
                        "job_id": job.get_id(),
                        "Results URL": url_for(
                            "api_v1.results", job_id=str(job.get_id()), _external=True
                        ),
                    }
                )

        return f(*args, **kwargs)

    return decorated


def validate_dates(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            json_doc = request.get_json()
            start_date = datetime_from_string(
                json_doc.get("start_date")).date()
            end_date = datetime_from_string(json_doc.get("end_date")).date()
            print(start_date)
            print(end_date)

            months_diff = number_of_months_between_2_dates(
                start_date, end_date)
            print(months_diff)
            if months_diff < 0:
                raise RequestError(
                    "Invalid dates provided! Starting date cannot be greater than end date."
                )
            if months_diff > 3:
                raise RequestError(
                    "Date range is too big. Please limit your search up to 3 months."
                )
        except ValueError:
            raise RequestError(
                "Invalid date string format provided! Please provide dates in the following format: dd/mm/AAAA"
            )

        return f(*args, **kwargs)

    return decorated
