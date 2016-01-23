import logging

from collections import namedtuple
from enum import IntEnum
from . import cgi
from .info import URL, DEFAULT_DIR


logger = logging.getLogger(__name__)


##################
# command.cgi API

def list_files(*filters, remote_dir=DEFAULT_DIR, url=URL):
    response = _get(Operation.list_files, url, DIR=remote_dir)
    files = _split_file_list(response.text)
    return (f for f in files if all(filt(f) for filt in filters))


def count_files(remote_dir=DEFAULT_DIR, url=URL):
    response = _get(Operation.count_files, url, DIR=remote_dir)
    return int(response.text)


def memory_changed(url=URL):
    """Returns True if memory has been written to, False otherwise"""
    response = _get(Operation.memory_changed, url)
    return int(response.text) == 1


#####################
# API implementation

_fields = ["directory", "filename", "size", "attribute", "date", "time"]
FileInfo = namedtuple("FileInfo", _fields)


def _split_file_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            d, f, *remaining = groups
            yield FileInfo(d, f, *map(int, remaining))


########################################
# command.cgi request prepping, sending

class Operation(IntEnum):
    list_files = 100
    count_files = 101
    memory_changed = 102


def _get(operation: Operation, url=URL, **params):
    """HTTP GET of the FlashAir command.cgi entrypoint"""
    prepped_request = _prep_get(operation, url=url, **params)
    return cgi.send(prepped_request)


def _prep_get(operation: Operation, url=URL, **params):
    params.update(op=int(operation))  # op param required
    return cgi.prep_get(cgi.Entrypoint.command, url=url, **params)

