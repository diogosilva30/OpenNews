import json
from flask import url_for
from flask_restx import Resource, Namespace, fields, inputs
from rq.job import Job as rqjob
from worker import conn


import app.core.common.custom_exceptions as custom_exceptions
from app.core import redis_queue
from app.core.common.models.job import Job
from app.core.common.decorator import prevent_duplicate_jobs
from app.core.common.helpers import to_list

from .services import publico_news_service
from .models.publico_news import PublicoNews
from .decorators import validate_urls, validate_topic_search

####################################################################################################################################
# API DECLARATION
api = Namespace('publico', description='Retrieve news from Publico (' +
                r'https://www.publico.pt' + ')')
####################################################################################################################################
# MODELS DECLARATION
job = api.model('Job', {
    'job_id': fields.String(required=True, description='The job id'),
    'Results URL': fields.String(attribute='job_url', required=True, description='Results URL'),
    'expires at': fields.DateTime(attribute='expires', required=True, description='Results expiration date'),
})
news = api.model('News', {
    'title': fields.String(required=True, description='News title'),
    'description': fields.String(required=True, description='News description'),
    'text': fields.String(required=True, description='News corpus'),
    'url': fields.String(required=True, description='News URL'),
    'date': fields.DateTime(required=True, description='News date and time'),
    'authors': fields.List(fields.String(description='Author name', required=True), description='List of authors', required=True)
})
topic_search = api.model('TopicSearch', {
    'searh topic': fields.String(attribute='search_topic', required=True, description="The topic used to search Publico's news"),
    'search start date': fields.Date(attribute='start_date', description='Topic search start date'),
    'search end date': fields.Date(attribute='end_date', description='Topic search end date'),
    'number of news': fields.Integer(attribute='number_of_news', description='Number of found news in topic search'),
    'news': fields.List(fields.Nested(news), attribute='found_news', description='List of found news')
})


####################################################################################################################################
# POST /topic_search -> Endpoint for searching news by topic
@api.doc(description="Searches news in Publico's website by topic. Consult " + r'https://www.publico.pt/topicos' + " for a list of valid topics.\n About the parameters: \n\t <strong>'start_date'\t: Required parameter</strong>. Indicates the starting date for topic search (format: dd/mm/AAAA).\n\t <strong>'end_date'\t\t : Required parameter</strong>. Indicates the ending date for topic search (format: dd/mm/AAAA).\n \t <em><strong>Important: </strong>(Due to the high ammount of required computations for this resource, the date range is limited to 3 months)</em>\n <strong>'search_topic'\t : Required</strong>. Indicates the topic to search news for")
@api.route('/topic_search')
class TopicSearch(Resource):
    # Parser to control expected input
    get_parser = api.parser()
    get_parser.add_argument('start_date', type=inputs.date_from_iso8601, required=True,
                            help='Starting date for topic search. (Expected string format: dd/mm/AAAA)', location='json')
    get_parser.add_argument('end_date', type=inputs.date_from_iso8601, required=True,
                            help='Ending date for topic search. (Expected string format: dd/mm/AAAA)', location='json')
    get_parser.add_argument('search_topic', type=str,
                            location='json', required=True)

    @validate_topic_search
    @prevent_duplicate_jobs
    @api.expect(get_parser)
    @api.marshal_with(job)
    @api.response(400, "A bad request was sent to the server.")
    # @token_required
    def post(self):
        """Creates job to retrieve Publico's news by topic"""
        # Add job to redis queue
        redis_job = redis_queue.enqueue(
            publico_news_service.search_by_topic, api.payload, result_ttl=10800, job_timeout=3*3600)  # kills job after 3 hours
        created_job = Job(redis_job.get_id(), url_for(
            'api_v1.results', job_id=redis_job.get_id(), _external=True), job_ttl=10800)
        return created_job
####################################################################################################################################


@api.doc(description="Searches news in Publico's website by specific URLs. ")
# @api.doc("This endpoint allows to extract news from a journal given the news URLs.")
@api.route('/')
class NewsbyURL(Resource):
    # Parser to control expected input
    get_parser = api.parser()
    # Add 'url' query param. Accepts multiple instances
    get_parser.add_argument('url', type=list,
                            help='News URL(s) to extract info.', location='json', required=True)

    @validate_urls
    @prevent_duplicate_jobs
    @api.expect(get_parser)
    @api.marshal_with(job)
    @api.doc(description='Retrieves news from a journal by URLs. These URLs should be as a <strong>JSON Array</strong> in request body.\n <strong>Important :</strong> URL search is limited to 50 URLs for each job.',)
    @api.response(200, description="News successfully fecthed by URLs")
    def post(self):
        """ Creates job to retrieve Publico's news by URLs"""
        # Make sure url fields is array
        # data = api.payload
        # for key, value in data.items():
        #     if key == 'url':
        #         data[key] = to_list(value)

        # if all urls are valid, add job to queue
        redis_job = redis_queue.enqueue(
            publico_news_service.search_by_urls, api.payload, result_ttl=10800, job_timeout=3*3600)  # kills job after 3 hours running
        created_job = Job(redis_job.get_id(), url_for(
            'api_v1.results', job_id=str(redis_job.get_id()), _external=True), job_ttl=10800)
        return created_job
