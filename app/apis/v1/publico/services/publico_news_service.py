import os
import json
from typing import List

from flask import request

from app.core.common.helpers import send_post_then_get_html_string, date_from_string, to_list
from ..models.publico_search import *
from ..models.publico_news import PublicoNews


def search_by_topic(data):
    """ Searhes Publico's website by a certain topic within a range of dates"""
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
    print("Starting to topic search news from Público with topic '{}' beetween dates {}<-->{}".format(
        search_topic, results.start_date, results.end_date))

    results.consume_api()

    return results


def search_by_urls(data: dict):
    """Extracts news from Publico's website by urls"""
    data = to_list(data.get(
        "url"))  # passed in query string args
    results = PublicoURLSearch()
    for url in data:
        results.add_news(url)
    return results


def search_by_keywords(data: dict):
    """ Searhes Publico's website with keywords within a range of dates"""
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
    print("Starting to search news from Público with keywords '{}' beetween dates {}<-->{}".format(
        keywords, results.start_date, results.end_date))

    results.consume_api()

    return results
