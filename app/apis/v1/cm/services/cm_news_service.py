"""
This module contains all the functions needed to route the requests under the CM's namespace.
"""

import json

from ..models.cm_search import CMTopicSearch


def search_by_topic(data: dict) -> CMTopicSearch:
    """ Searhes news in CM's website by a certain topic within a range of dates.

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the topic search.

    Returns
    -------
    results
        'CMTopicSearch' object containing the request information and it's results.
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
    results = CMTopicSearch(search_topic, start_date, end_date)
    # Log topic search start
    print(
        "Starting to topic search news from CM's website with topic '{}' beetween dates {}<-->{}".format(
            search_topic, results.start_date, results.end_date
        )
    )
    # Perform the search
    results.search()

    return results
