from flask_restx import Namespace, Resource
from .results_service import get_results


####################################################################################################################################
# API DECLARATION
api = Namespace("results", description="Retrieve results from jobs")

####################################################################################################################################


@api.doc(description="Retrieves results from a job.")
@api.param(name="job_id", description="The assigned job_id after a POST request")
@api.route("/<job_id>", endpoint="results")
class ResultsURLSearch(Resource):
    @api.response(200, "Sucessfuly retrieved the job results")
    @api.response(202, "Job is accepted but still waiting to be processed")
    @api.response(404, "Job does not exist")
    def get(self, job_id):
        """Retrieves results from a job
        <em><strong>Important:</strong> These results are only kept in registry for 3 hours. After this timespan they get deleted and a new request must be made.</em>
        """
        return get_results(job_id)
