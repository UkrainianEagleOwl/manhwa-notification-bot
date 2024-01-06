from datetime import datetime, timedelta
import dateparser


def parse_relative_time(time_string):
    """
    Parses relative time strings like "2 mins ago" into a datetime object.
    If the parsing fails or the field is empty, returns None.
    """
    if time_string:
        # The dateparser library can parse relative time strings into datetime objects
        # The 'SETTINGS' parameter tells dateparser to assume the relative time is in the past
        return dateparser.parse(
            time_string,
            settings={"RELATIVE_BASE": datetime.utcnow(), "PREFER_DATES_FROM": "past"},
        )
    return None
