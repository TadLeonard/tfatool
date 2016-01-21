import logging
from collections import namedtuple
from enum import IntEnum
from . import cgi
from .info import URL, DEFAULT_DIR


logger = logging.getLogger(__name__)


class Op(IntEnum):
    list_files = 100
    count_files = 101


def get(op: Op, url=URL, **params):
    params.update(op=op)
    return cgi.get(cgi.Entrypoint.command, url=url, **params)


##################
# command.cgi API


def list_files(*filters, remote_dir=DEFAULT_DIR, url=URL):
    response = get(Op.list_files, url, DIR=remote_dir)
    files = _split_file_list(response.text)
    return (f for f in files if all(filt(f) for filt in filters))


def count_files(remote_dir=DEFAULT_DIR, url=URL):
    response = get(Op.count_files, url, DIR=remote_dir)
    return int(response.text)


#####################
# API implementation


_fields = ["directory", "filename", "size", "attribute", "date", "time"]
FileInfo = namedtuple("FileInfo", _fields)


def _split_file_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            d, f, size, a, date, time = groups
            yield FileInfo(d, f, int(size), a, int(date), int(time))


