import dateparser
from datetime import datetime, date


def datetime_from_string(date_string: str, order="DMY") -> datetime:
    """Parses a str to datetime. Assumes format: dd/mm/YYYY by default"""

    if isinstance(date_string, (datetime, date)):
        return date_string
    return dateparser.parse(date_string, settings={"DATE_ORDER": order})
