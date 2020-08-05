import os
import json
from typing import List

from flask import request

from app.apis.v1.publico.models.publico_news import PublicoNews
from app.core.common.helpers import send_post_then_get_html_string, date_from_string, to_list
from ..models.publico_search import PublicoTopicSearch, PublicoURLSearch

payload = {'username': os.getenv('PUBLICO_USER'),
           "password": os.getenv('PUBLICO_PW')}


def search_by_topic(data):
    """ Searhes Publico's website by a certain topic within a range of dates"""
    json_doc = json.loads(json.dumps(data))
    # Extract variables from data
    search_topic = json_doc.get("search_topic").replace("\n", "")
    start_date = json_doc.get("start_date")
    end_date = json_doc.get("end_date")
    results = PublicoTopicSearch(search_topic, start_date, end_date)
    # Log topic search start
    print("Starting to topic search news from Público with topic '{}' beetween dates {}<-->{}".format(
        search_topic, results.start_date, results.end_date))
    page_number = 1
    # Flag used to stop the search
    stop_entire_search = False
    while (r := send_post_then_get_html_string(post_url="https://www.publico.pt/api/user/login", post_payload=payload, get_url=("https://www.publico.pt/api/list/" +
                                                                                                                                search_topic.replace(" ", "-").lower() + "?page=" + str(page_number)))
           ) != "[]":
        print("Now reading page number {}...".format(page_number))
        # Read the json data
        data = json.loads(r)
        # iterate over each news dict and create a News object from it
        for item in data:
            # Found news out of lower bound date, STOP THE SEARCH!
            if PublicoNews.parse_date(item.get("data")) < results.start_date:
                stop_entire_search = True
                break  # stop the local search
            # Found news more recent that end date, SKIP AHEAD
            elif PublicoNews.parse_date(item.get("data")) > results.end_date:
                continue
            # Found news inside the date rage, add to list
            else:
                results.add_news(item)
        if stop_entire_search:
            break
        page_number = page_number+1
    print("Found {} news!".format(str(len(results.found_news))))
    return results


def search_by_urls(data: str):
    """Extracts news from Publico's website by urls"""
    data = to_list(data.get(
        "url"))  # passed in query string args
    results = PublicoURLSearch()
    for url in data:
        results.add_news(url)
    return results
