""" This module provided small auxiliary function used across the application"""
from datetime import date, time, datetime
import dateparser
from flask.helpers import url_for
from flask.json import jsonify
import requests


def normalize_str(string):
    """ Removes extra white space, removes backslash '\\' and removes '\\n' and '\\r'"""
    return (
        " ".join(string.split()).replace("\n", "").replace("\r", "").replace("\\", "")
    )


def datetime_from_string(date_string: str, order="DMY") -> datetime:
    """Parses a str to datetime. Assumes format: dd/mm/YYYY by default"""

    if isinstance(date_string, (datetime, date)):
        return date_string
    return dateparser.parse(date_string, settings={"DATE_ORDER": order})


def custom_json_serializer(obj):
    """ Provides custom serialization to JSON"""
    if isinstance(obj, (datetime, time)):
        return obj.isoformat()

    if hasattr(obj, "__dict__"):
        return obj.__dict__

    return None


def results_response(job_id: str):
    """ Generates a results response for a given 'job_id'"""

    return jsonify(
        {
            "status": "ok",
            "job_id": job_id,
            "Results URL": url_for("api_v1.results", job_id=job_id, _external=True),
        }
    )


def validate_url(url: str) -> bool:
    """Validates if an URL exists (returns 200 status code)

    Parameters
    ----------
    url : str
        URL to validate"""
    try:
        if requests.get(url).status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        return False


def to_list(obj):
    """ Transforms a object into list. If object is already a list, it stays the same"""
    return obj if isinstance(obj, list) else [obj]


def number_of_months_between_2_dates(start_date: datetime, end_date: datetime) -> int:
    """
    Calculates the number of months beetween 2 dates

    Parameters
    ----------
    start_date: datetime
        Starting date
    end_date: datetime
        Ending date

    Returns
    -------
    int
        Number of months
    """
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
