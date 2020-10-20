"""
This module contains all the functions needed to route the requests under the CM's namespace.
"""

from app.core.common.helpers import to_list
import json

import numpy as np

from ..models import CMSearch


def search_by_tag(data: dict) -> dict:
    """Searhes news in CM's website by a certain tag within a range of dates.

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the tag search.

    Returns
    -------
    results
        dict object containing the request information and it's results.
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

    # Log topic search start
    print(
        "Starting to topic search news from CM's website with topic '{}' beetween dates {}<-->{}".format(
            search_topic, start_date, end_date
        )
    )
    # Perform the search
    return CMSearch().tag_search(search_topic, start_date, end_date)


def search_by_urls(data: dict) -> dict:
    """Searhes news in CM's website by URL(s).

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the URL(s) search.

    Returns
    -------
    dict
        dictionary containing the request information and it's results.
    """

    # Transform dict object into a list of URL(s)
    data = np.unique(to_list(data.get("url")))

    # Log keywords search start
    print(f"Starting to search news by URLs {len(data)} from CM")

    return CMSearch().url_search(data)
