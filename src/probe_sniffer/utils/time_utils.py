import pytz
from datetime import datetime


def get_log_time():
    """
    Returns date and 12HR time in timezone e.g. 03/12/2024 09:14:44 PM
    """
    bst = pytz.timezone("America/New_York")
    date = str(datetime.now(bst).strftime("%Y-%m-%d"))
    clock = str(datetime.now(bst).isoformat().replace("T", "").split(".")[0])
    log_clock = clock[-8:]
    log_time = str(date + " " + log_clock)
    return log_time
