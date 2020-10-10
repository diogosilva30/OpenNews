from datetime import date, time, datetime
import dateparser
import requests


def validate_url(url) -> bool:
    """ Send HTTP GET request to a certain a URL and checks for 200 status code"""
    return requests.get(url).status_code == 200


def normalize_str(string):
    """ Removes extra white space, removes backslash '\\' and removes '\\n' and '\\r'"""
    return (
        " ".join(string.split()).replace(
            "\n", "").replace("\r", "").replace("\\", "")
    )


def datetime_from_string(x: str) -> datetime:
    """Parses a str to datetime"""

    if isinstance(x, (datetime, date)):
        return x
    return dateparser.parse(x)


def custom_json_serializer(obj):
    if isinstance(obj, (datetime, time)):
        return obj.isoformat()

    elif hasattr(obj, "__dict__"):
        return obj.__dict__


def send_post_then_get_html_string(post_url, post_payload, get_url):
    """Sends an HTTP Post to a certain URL, then sends a HTTP Get to another URL, and returns the obtained HTML string"""
    with requests.Session() as s:
        s.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"
            }
        )
        # send POST request to login
        s.post(post_url, data=post_payload)
        return s.get(get_url)


def to_list(x):
    if isinstance(x, list):
        return x
    else:
        return [x]


def number_of_months_between_2_dates(start_date: datetime, end_date: datetime) -> int:
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
