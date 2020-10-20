"""
This module contains all the functions needed to route the requests under the Publico's namespace.
"""

import json
import numpy as np

from app.core.common.helpers import to_list
from ..models import PublicoSearch


def search_by_tag(data: dict) -> dict:
    """Searhes news in Publico's website by a certain tag within a range of dates.

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the tag search.

    Returns
    -------
    dict
        dictionary containing the request information and it's results.
    """
    # Load API payload into JSON doc
    json_doc = json.loads(json.dumps(data))
    # Extract search topic from JSON
    search_topic = json_doc.get("search_topic").replace("\n", "")
    # Extract start date from JSON
    start_date = json_doc.get("start_date")
    # Extract end date from JSON
    end_date = json_doc.get("end_date")

    # Log tag search start
    print(
        f"Starting to topic search news from Público with topic '{search_topic}' beetween dates {start_date}<-->{end_date}"
    )
    return PublicoSearch().tag_search(search_topic, start_date, end_date)


def search_by_keywords(data: dict) -> dict:
    """Searhes news in Publico's website by keywords within a range of dates.

    Parameters
    ----------
    data
        Dictionary containing the POST request payload for the URL(s) search.

    Returns
    -------
    dict
        dictionary containing the request information and it's results.
    """
    # Load API payload into JSON doc
    json_doc = json.loads(json.dumps(data))
    # Extract keywords
    keywords = json_doc.get("keywords").replace("\n", "")
    # Extract start date
    start_date = json_doc.get("start_date")
    # Extract end date
    end_date = json_doc.get("end_date")

    # Log keywords search start
    print(
        f"Starting to search news from Público with keywords '{keywords}' beetween dates {start_date}<-->{end_date}"
    )
    return PublicoSearch().keyword_search(keywords, start_date, end_date)


def search_by_urls(data: dict) -> dict:
    """Searhes news in Publico's website by URL(s).

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
    print(f"Starting to search news by URLs {len(data)} from Público")

    return PublicoSearch().url_search(data)
