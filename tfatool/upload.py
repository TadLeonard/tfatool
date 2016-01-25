import os
import arrow
from . import cgi
from .info import DEFAULT_DIR, DEFAULT_MASTERCODE, URL


def upload_file(local_path: str, url=URL, dest=DEFAULT_DIR):
    ctime = os.stat(local_path).st_ctime
    fat_time = _encode_ctime(ctime)


def _encode_time(ctime: float):
    """Encode a ctime float as a 32-bit FAT time"""
    dt = arrow.get(ctime)
    date_val = ((dt.year - 1980) << 9) | (dt.month << 5) | dt.day
    time_val = (dt.hour << 11) | (dt.minute << 6) | int(dt.second / 2)
    return date_val << 16 | time_val

