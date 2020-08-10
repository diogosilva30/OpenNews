from datetime import time, datetime, date
from typing import Any

# needs pip install python-dateutil
import dateutil.parser
import requests

from app.core.common.custom_exceptions import RequestError


def validate_url(url, contains=None) -> bool:
    try:
        if contains is None:
            return requests.get(url).status_code == 200
        else:
            print(requests.get(url).status_code)
            return requests.get(url).status_code == 200 and contains in url
    except:
        raise RequestError("URL '{}' is not valid!")


def datetime_from_string(x: str) -> datetime:
    if isinstance(x, datetime):
        return x

    return dateutil.parser.parse(x)


def date_from_string(x: str) -> date:
    if isinstance(x, date):
        return x.date()
    return dateutil.parser.parse(x, dayfirst=True).date()


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def custom_json_serializer(obj):
    if isinstance(obj, (datetime, time)):
        return obj.isoformat()

    elif hasattr(obj, '__dict__'):
        return obj.__dict__


def send_post_then_get_html_string(post_url, post_payload, get_url):
    """Sends an HTTP Post to a certain URL, then sends a HTTP Get to another URL, and returns the obtained HTML string"""
    # TODO Remove this
    print(get_url)
    with requests.Session() as s:
        s.headers.update(
            {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'})
        # send POST request to login
        s.post(post_url, data=post_payload)
        return s.get(get_url).text


def to_list(x):
    if isinstance(x, list):
        return x
    else:
        return [x]


def number_of_months_between_2_dates(start_date: datetime, end_date: datetime) -> int:
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
