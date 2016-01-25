import math
import os
import arrow

from functools import partial

from . import cgi
from .info import DEFAULT_DIR, DEFAULT_MASTERCODE, URL
from .info import WriteProtectMode, Upload, ResponseCode
from requests import RequestException


def upload_file(local_path: str, url=URL, dest=DEFAULT_DIR):
    wp = set_write_protect(WriteProtectMode.on, url=url)
    if wp.text != ResponseCode.success:
        raise RequestException("Failed to set write protect")
    ud = set_upload_dir(dest, url=url)
    if ud.text != ResponseCode.success:
        raise RequestException("Failed to set upload directory")
    ct = set_creation_time(local_path, url=url)
    if ud.text != ResponseCode.success:
        raise RequestException("Failed to set creation time")
    pf = post_file(local_path, url=url)
    if pf.text != ResponseCode.success:
        raise RequestException("Failed to post file")


def set_write_protect(mode: WriteProtectMode, url=URL):
    return post(url=url, **{Upload.write_protect: mode})


def set_remote_dir(remote_dir: str, url=URL):
    return post(url=url, **{Upload.directory: remote_dir})


def set_creation_time(local_path: str, url=URL):
    ctime = os.stat(local_path).st_ctime
    fat_time = _encode_ctime(ctime)
    encoded_time = _str_encode_time(fat_time)
    return post(url=url, **{Upload.creation_time: encoded_time})


def post_file(local_path: str, url=URL):
    files = {local_path: open(local_path, "rb")}
    return post(url=url, req_kwargs=dict(files=files))


def delete_file(remote_file: str, url=URL):
    return post(url=url, **{Upload.delete: remote_file})


def post(url=URL, req_kwargs=None, **params):
    req_kwargs = req_kwargs or {}
    params = {key.name: value for key, value in params.items()}
    prepped_reqeust = _prep_post(url=url, req_kwargs=req_kwargs, **params)
    return cgi.send(prepped_request)


_prep_post = partial(cgi.prep_post, cgi.Entrypoint.upload)


def _str_encode_time(encoded_time: int):
    return "{0:#0{1}x}".format(encoded_time, 10)


def _encode_time(ctime: float):
    """Encode a ctime float as a 32-bit FAT time"""
    dt = arrow.get(ctime)
    date_val = ((dt.year - 1980) << 9) | (dt.month << 5) | dt.day
    secs = dt.second + dt.microsecond / 10**6
    time_val = (dt.hour << 11) | (dt.minute << 6) | math.floor(secs / 2)
    return (date_val << 16) | time_val

