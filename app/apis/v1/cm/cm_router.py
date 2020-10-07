from flask import url_for, jsonify
from flask_restx import Resource, Namespace, inputs

from app.core import redis_queue
from app.core.common.decorators import prevent_duplicate_jobs

from app.core.common.decorators import validate_dates
from .services import cm_news_service

####################################################################################################################################
# NAMESPACE DECLARATION
api = Namespace(
    "cm",
    description="Retrieve news from Correio da Manhã (CM) (" +
    r"https://www.cmjornal.pt" + ")",
)

####################################################################################################################################
# POST /topic_search -> Endpoint for searching news by topic


@api.doc(description="Searches news in CM's website by <strong>topic</strong>.")
@api.route("/topic_search")
class TopicSearch(Resource):
    # Parser to control expected input
    parser = api.parser()
    parser.add_argument(
        "start_date",
        type=inputs.date_from_iso8601,
        required=True,
        help="Starting date for topic search. (Expected string format: dd/mm/AAAA)",
        location="json",
    )
    parser.add_argument(
        "end_date",
        type=inputs.date_from_iso8601,
        required=True,
        help="Ending date for topic search. (Expected string format: dd/mm/AAAA)",
        location="json",
    )
    parser.add_argument("search_topic", type=str,
                        location="json", required=True)

    @validate_dates
    @prevent_duplicate_jobs
    @api.expect(parser)
    @api.response(200, description="News successfully fetched by topic.")
    @api.response(
        400, description="Bad request, selected dates are invalid or range is too high."
    )
    def post(self):
        """Creates job to retrieve Publico's news by topic

        <em><strong>Important: </strong>Due to the high ammount of required computations for this resource, the date range is limited to 3 months.
        This resource may seem equal to <strong>keywords search</strong>. However, this resource gives <strong>narrower (more accurate) results</strong>, as it <strong>only</strong> includes news related to the topic.</em>

         About the parameters:
         <strong>'start_date' : Required parameter</strong>. Indicates the starting date for topic search (format: dd/mm/AAAA).
         <strong>'end_date' : Required parameter</strong>. Indicates the ending date for topic search (format: dd/mm/AAAA).
         <strong>'search_topic' : Required</strong>. Indicates the topic to search news for. Consult https://www.publico.pt/topicos for a list of valid topics.

        <strong>Usage examples (POST JSON body)</strong>:\n
        Searching for the topic "luanda leaks" between 01/01/2020 and 05/03/2020:
        {
            "start_date" : "1/1/2020",
            "end_date" : "5/3/2020",
            "search_topic" : "luanda leaks"
        }
        """
        # Add job to redis queue
        redis_job = redis_queue.enqueue(
            cm_news_service.search_by_topic,
            api.payload,
            result_ttl=10800,
            job_timeout=3 * 3600,
        )  # kills job after 3 hours
        return jsonify(
            {
                "status": "ok",
                "job_id": redis_job.get_id(),
                "Results URL": url_for(
                    "api_v1.results", job_id=redis_job.get_id(), _external=True
                ),
            }
        )
