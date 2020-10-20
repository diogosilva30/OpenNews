""" This modules routes the CM's requests to the
corresponding services"""
from flask_restx import Resource, Namespace
from app.core.common.helpers import results_response
from app.core import cm_queue
from app.core.common.decorators import (
    validate_dates,
    prevent_duplicate_cm_jobs,
    validate_urls,
)
from app.core.common.parsers import tag_search_parser, url_search_parser
from .services import cm_news_service

api = Namespace(
    "cm",
    description="Retrieve news from Correio da Manhã (CM) ("
    + r"https://www.cmjornal.pt"
    + ")",
)

# POST /tag_search -> Endpoint for searching news by tag
@api.doc(description="Searches news in CM's website by <strong>tag</strong>.")
@api.route("/tag_search")
class TagSearch(Resource):
    @validate_dates
    @prevent_duplicate_cm_jobs
    @api.expect(tag_search_parser(api))
    @api.response(200, description="News successfully fetched by tag.")
    @api.response(
        400, description="Bad request, selected dates are invalid or range is too high."
    )
    def post(self):
        """Creates job to retrieve CM's news by tag

        <em><strong>Important: </strong>Due to the high ammount of required computations for this resource, the date range is limited to 3 months.
        This resource may seem equal to <strong>keywords search</strong>. However, this resource gives <strong>narrower (more accurate) results</strong>, as it <strong>only</strong> includes news related to the tag.</em>

         About the parameters:
         <strong>'start_date' : Required parameter</strong>. Indicates the starting date for tag search (format: dd/mm/AAAA).
         <strong>'end_date' : Required parameter</strong>. Indicates the ending date for tag search (format: dd/mm/AAAA).
         <strong>'tag' : Required</strong>. Indicates the tag to search news for.

        <strong>Usage examples (POST JSON body)</strong>:\n
        Searching for the tag "luanda leaks" between 01/01/2020 and 05/03/2020:
        {
            "start_date" : "1/1/2020",
            "end_date" : "5/3/2020",
            "tag" : "luanda leaks"
        }
        """
        # Add job to redis queue
        redis_job = cm_queue.enqueue(
            cm_news_service.search_by_tag,
            api.payload,
            result_ttl=10800,
            job_timeout=3 * 3600,
        )  # kills job after 3 hours
        return results_response(redis_job.get_id())


@api.doc(
    description="Searches news in CM's website by specific URLs.\n \
     <strong>Important :</strong> URL search is limited to 50 URLs for each job."
)
@api.route("/")
class URLSearch(Resource):
    @validate_urls
    @prevent_duplicate_cm_jobs
    @api.expect(url_search_parser(api))
    @api.response(200, description="News successfully fetched by URLs.")
    @api.response(400, description="Bad request, URLs are invalid or unsupported.")
    def post(self):
        """Creates job to retrieve CM's news by URLs
        About the parameters:
         \n\t <strong>'url'\t: Required parameter</strong>. Indicates the news URL(s) to search. In the case of multiple URLs these should be passed as a <strong>JSON Array</strong> in the request body. See the examples below.\n

        <strong>Usage examples (POST JSON body)</strong>:\n
        Searching for only <strong>one</strong> URL:
        {
            "url" : "https://www.cmjornal.pt/sociedade/detalhe/alerta-cm--portugal-ultrapassa-os-100-mil-infetados-por-covid-19-1949-novos-casos-e-17-mortos-nas-ultimas-24-horas"
        }

        Searching for <strong>two</strong> URLs:
        {
            "url" : [ "https://www.cmjornal.pt/sociedade/detalhe/alerta-cm--portugal-ultrapassa-os-100-mil-infetados-por-covid-19-1949-novos-casos-e-17-mortos-nas-ultimas-24-horas", \
            "https://www.cmjornal.pt/famosos/detalhe/margarida-corceiro-constroi-casa-milionaria-aos-17-anos" ]
        }
        """
        redis_job = cm_queue.enqueue(
            cm_news_service.search_by_urls,
            api.payload,
            result_ttl=10800,
            job_timeout=3 * 3600,
        )  # kills job after 3 hours running
        return results_response(redis_job.get_id())
