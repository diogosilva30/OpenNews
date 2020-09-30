from flask_restx import Namespace, Resource
from rq.job import Job as rqjob

import app.core.common.custom_exceptions as custom_exceptions
from worker import conn


####################################################################################################################################
# API DECLARATION
api = Namespace('results', description='Retrieve results from jobs')

####################################################################################################################################


@api.doc(description="Retrieves results from a job.")
@api.param(name='job_id', description='The assigned job_id after a POST request')
@api.route('/<job_id>', endpoint='results')
class ResultsURLSearch(Resource):
    @api.response(200, 'Sucessfuly retrieved the job results')
    @api.response(202, 'Job is accepted but still waiting to be processed')
    @api.response(404, 'Job does not exist')
    def get(self, job_id):
        """ Retrieves results from a job
        <em><strong>Important:</strong> These results are only kept in registry for 3 hours. After this timespan they get deleted and a new request must be made.</em>
        """
        print("JOB iD", job_id)
        try:
            fetched_job = rqjob.fetch(job_id, connection=conn)

        except:
            raise custom_exceptions.ResourceNotFound(
                "Job {} does not exist!".format(job_id))

        print(fetched_job)
        if fetched_job.is_finished:
            return fetched_job.result.serialize_to_json()
        else:
            raise custom_exceptions.StillProcessing(
                "Job {} has not been processed yet, try again later!".format(job_id))
