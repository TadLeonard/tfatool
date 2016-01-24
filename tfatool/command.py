import logging
import arrow

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


def get_ssid(url=URL):
    return _get(Operation.get_ssid, url).text


def get_password(url=URL):
    return _get(Operation.get_password, url).text


def get_mac(url=URL):
    return _get(Operation.get_mac, url).text





#####################
# API implementation

FileInfo = namedtuple(
    "FileInfo", "directory filename size attribute datetime")


def _split_file_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            directory, filename, *remaining = groups
            remaining = map(int, remaining)
            size, attr_val, date_val, time_val = remaining
            timeinfo = _decode_time(date_val, time_val)
            attribute = _decode_attribute(attr_val)
            yield FileInfo(directory, filename,
                           size, attribute, timeinfo)


def _decode_time(date_val: int, time_val: int):
    year = (date_val >> 9) + 1980  # 0-val is the year 1980
    month = (date_val & (0b1111 << 5)) >> 5
    day = date_val & 0b11111
    hour = time_val >> 11
    minute = (time_val & (0b111111 << 6)) >> 6
    second = (time_val & 0b11111) * 2
    return arrow.get(year, month, day, hour, minute, second)


AttrInfo = namedtuple(
    "AttrInfo", "archive directly volume system_file hidden_file read_only")

def _decode_attribute(attr_val: int):
    bit_positions = reversed(range(6))
    bit_flags = [bool(attr_val & (1 << bit)) for bit in bit_positions]
    return AttrInfo(*bit_flags)


########################################
# command.cgi request prepping, sending

class Operation(IntEnum):
    list_files = 100
    count_files = 101
    memory_changed = 102
    get_ssid = 104
    get_password = 105
    get_mac = 106
    


def _get(operation: Operation, url=URL, **params):
    """HTTP GET of the FlashAir command.cgi entrypoint"""
    prepped_request = _prep_get(operation, url=url, **params)
    return cgi.send(prepped_request)


def _prep_get(operation: Operation, url=URL, **params):
    params.update(op=int(operation))  # op param required
    return cgi.prep_get(cgi.Entrypoint.command, url=url, **params)

