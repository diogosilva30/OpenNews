""" This modules routes the Publico's requests to the
corresponding services"""

from flask_restx import Resource, Namespace
from app.core.common.helpers import results_response
from app.core import publico_queue
from app.core.common.decorators import (
    validate_dates,
    prevent_duplicate_publico_jobs,
    validate_urls,
)
from app.core.common.parsers import (
    url_search_parser,
    keywords_search_parser,
    tag_search_parser,
)
from .services import publico_news_service


api = Namespace(
    "publico",
    description="Retrieve news from Publico (" + r"https://www.publico.pt" + ")",
)

# POST /tag_search -> Endpoint for searching news by tag
@api.doc(description="Searches news in Publico's website by <strong>tag</strong>.")
@api.route("/tag_search")
class TagSearch(Resource):
    @validate_dates
    @prevent_duplicate_publico_jobs
    @api.expect(tag_search_parser(api))
    @api.response(200, description="News successfully fetched by tag.")
    @api.response(
        400, description="Bad request, selected dates are invalid or range is too high."
    )
    def post(self):
        """Creates job to retrieve Publico's news by tag

        <em><strong>Important: </strong>Due to the high ammount of required computations for this resource, the date range is limited to 3 months.
        This resource may seem equal to <strong>keywords search</strong>. However, this resource gives <strong>narrower (more accurate) results</strong>, as it <strong>only</strong> includes news related to the tag.</em>

         About the parameters:
         <strong>'start_date' : Required parameter</strong>. Indicates the starting date for tag search (format: dd/mm/AAAA).
         <strong>'end_date' : Required parameter</strong>. Indicates the ending date for tag search (format: dd/mm/AAAA).
         <strong>'tag' : Required</strong>. Indicates the tag to search news for. Consult https://www.publico.pt/topicos for a list of valid tags.

        <strong>Usage examples (POST JSON body)</strong>:\n
        Searching for the tag "luanda leaks" between 01/01/2020 and 05/03/2020:
        {
            "start_date" : "1/1/2020",
            "end_date" : "5/3/2020",
            "tag" : "luanda leaks"
        }
        """
        # Add job to redis queue
        redis_job = publico_queue.enqueue(
            publico_news_service.search_by_tag,
            api.payload,
            result_ttl=10800,
            job_timeout=3 * 3600,
        )  # kills job after 3 hours

        return results_response(redis_job.get_id())


# POST / -> Endpoint for searching news by Keywords
@api.doc(description="Searches news in Publico's website by <strong>keywords</strong>.")
@api.route("/keywords_search")
class NewsbyKeywords(Resource):
    @validate_dates
    @prevent_duplicate_publico_jobs
    @api.expect(keywords_search_parser(api))
    @api.response(200, description="News successfully fetched by keywords.")
    @api.response(
        400, description="Bad request, selected dates are invalid or range is too high."
    )
    def post(self):
        """Creates job to retrieve Publico's news by keywords

        <em><strong>Important: </strong>Due to the high ammount of required computations for this resource, the date range is limited to 3 months.
        This resource may seem equal to <strong>tag search</strong>. However, this resource gives <strong>broader results</strong>, as it includes <strong>every</strong> news that contains <strong>any</strong> of the keywords.</em>

        About the parameters:
         <strong>'start_date' : Required parameter</strong>. Indicates the starting date for keywords search (format: dd/mm/AAAA).
         <strong>'end_date' : Required parameter</strong>. Indicates the ending date for keywords search (format: dd/mm/AAAA).
         <strong>'keywords' : Required parameter</strong>. Indicates the keywords to search news for.

        <strong>Usage examples (POST JSON body)</strong>:\n
        Searching for the keyword "covid" between 01/01/2020 and 05/03/2020:
        {
            "start_date" : "1/1/2020",
            "end_date" : "5/3/2020",
            "keywords" : "covid"
        }
        Searching for the keywords "corona virus" between 01/01/2020 and 05/03/2020:
        {
            "start_date" : "1/1/2020",
            "end_date" : "5/3/2020",
            "keywords" : "corona virus"
        }

        """
        redis_job = publico_queue.enqueue(
            publico_news_service.search_by_keywords,
            api.payload,
            result_ttl=10800,
            job_timeout=3 * 3600,
        )  # kills job after 3 hours running
        return results_response(redis_job.get_id())


# POST / -> Endpoint for searching news by URLs


@api.doc(
    description="Searches news in Publico's website by specific URLs.\n \
     <strong>Important :</strong> URL search is limited to 50 URLs for each job."
)
@api.route("/")
class NewsbyURL(Resource):
    @validate_urls
    @prevent_duplicate_publico_jobs
    @api.expect(url_search_parser(api))
    @api.response(200, description="News successfully fetched by URLs.")
    @api.response(400, description="Bad request, URLs are invalid or unsupported.")
    def post(self):
        """Creates job to retrieve Publico's news by URLs
        About the parameters:
         \n\t <strong>'url'\t: Required parameter</strong>. Indicates the news URL(s) to search. In the case of multiple URLs these should be passed as a <strong>JSON Array</strong> in the request body. See the examples below.\n

        <strong>Usage examples (POST JSON body)</strong>:\n
        Searching for only <strong>one</strong> URL:
        {
            "url" : "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416"
        }

        Searching for <strong>two</strong> URLs:
        {
            "url" : [ "https://www.publico.pt/2020/08/10/local/noticia/estudo-aponta-residuos-perigosos-novas-obras-parque-nacoes-1927416", \
            "https://www.publico.pt/2020/08/10/sociedade/noticia/ordem-medicos-recomenda-mascaras-rua-testes-contactos-risco-1927613" ]
        }
        """
        redis_job = publico_queue.enqueue(
            publico_news_service.search_by_urls,
            api.payload,
            result_ttl=10800,
            job_timeout=3 * 3600,
        )  # kills job after 3 hours running
        return results_response(redis_job.get_id())
