"""
This module contains all the functions needed to route the requests under the Publico's namespace.
"""

import json
import numpy as np

from app.core.common.helpers import to_list
from ..models.publico_search import (
    PublicoTopicSearch,
    PublicoURLSearch,
    PublicoKeywordsSearch,
)


def search_by_topic(data: dict) -> PublicoTopicSearch:
    """Searhes news in Publico's website by a certain topic within a range of dates.

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the topic search.

    Returns
    -------
    results
        'PublicoTopicSearch' object containing the request information and it's results.
    """
    # Load API payload into JSON doc
    json_doc = json.loads(json.dumps(data))
    # Extract search topic from JSON
    search_topic = json_doc.get("search_topic").replace("\n", "")
    # Extract start date from JSON
    start_date = json_doc.get("start_date")
    # Extract end date from JSON
    end_date = json_doc.get("end_date")
    # Create TopicSearch object
    results = PublicoTopicSearch(search_topic, start_date, end_date)
    # Log topic search start
    print(
        "Starting to topic search news from Público with topic '{}' beetween dates {}<-->{}".format(
            search_topic, results.start_date, results.end_date
        )
    )
    # Consume the Publico's API
    results.consume_api()

    return results


def search_by_keywords(data: dict) -> PublicoKeywordsSearch:
    """Searhes news in Publico's website by keywords within a range of dates.

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the URL(s) search.

    Returns
    -------
    results
        'PublicoURLSearch' object containing the request information and it's results.
    """
    # Load API payload into JSON doc
    json_doc = json.loads(json.dumps(data))
    # Extract keywords
    keywords = json_doc.get("keywords").replace("\n", "")
    # Extract start date
    start_date = json_doc.get("start_date")
    # Extract end date
    end_date = json_doc.get("end_date")
    # Create KeywordsSearch object
    results = PublicoKeywordsSearch(keywords, start_date, end_date)

    # Log topic search start
    print(
        "Starting to search news from Público with keywords '{}' beetween dates {}<-->{}".format(
            keywords, results.start_date, results.end_date
        )
    )

    # Consume Publico's API
    results.consume_api()

    return results


def search_by_urls(data: dict) -> PublicoURLSearch:
    """Searhes news in Publico's website by URL(s).

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the URL(s) search.

    Returns
    -------
    results
        'PublicoURLSearch' object containing the request information and it's results.
    """
    # Transform dict object into a list of URL(s)
    data = np.unique(to_list(data.get("url")))
    # Create URLSearch object
    results = PublicoURLSearch()
    # For each URL add the news
    for url in data:
        results.add_news(url)

    return results
