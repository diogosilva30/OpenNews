from flask import Blueprint
from flask_restx import Api

import app.core.common.custom_exceptions as custom_exceptions
from .cm import cm_api
from .publico import publico_api
from .results import results_api

blueprint_api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


api = Api(
    blueprint_api_v1,
    title="Portuguese News Extractor API",
    version="1.0",
    description="An open-source REST API that extracts news, from portuguese jornals, to JSON.\n To extract news a POST request must be made to specific endpoints under a journal's namespace. \
              Due to the high computations that may be required to extract news, the results are not returned in the response. Instead a 'job' is queued for process in the background, and it's processed when possible. \
                  So a 'job_id' is returned regarding the request made. These results can then be obtained with a GET request under the results namespace.\n \
                  Check out the <a href='https://github.com/spamz23/API-NEWS_EXTRACTOR'> GitHub </a> repo and feel free to contribute.",
)

api.add_namespace(publico_api, path="/news/publico")
api.add_namespace(cm_api, path="/news/cm")
api.add_namespace(results_api, path="/news/results")


@api.errorhandler(custom_exceptions.RequestError)
def handle_value_error_exception(error):
    """Return a custom message and 400 (bad request) status code"""
    return {"status": "error", "message": str(error)}, 400  # bad request


@api.errorhandler(custom_exceptions.ResourceNotFound)
def handle_not_found_exception(error):
    """Return a custom message and 404(not found) status code"""
    return {"status": "error", "message": str(error)}, 404  # not found


@api.errorhandler(custom_exceptions.StillProcessing)
def handle_still_processing_exception(error):
    """Return a custom message and 202(accepted) status code"""
    return {"status": "ok", "message": str(error)}, 202  # accepted


@api.errorhandler(custom_exceptions.FailedJob)
def handle_failed_job_exception(error):
    """Return a custom message and 500(error) status code"""
    return {"status": "error", "message": str(error)}, 500 # error
