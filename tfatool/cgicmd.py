import logging
import requests
from collections import namedtuple
from enum import Enum


logger = logging.getLogger(__name__)


##################################
# FlashAir API request formatting


URL = "http://flashair"
DEFAULT_DIR = "/DCIM/100__TSB"


class Op(Enum):
    list_files = 100
    count_files = 101


def make_cmd(op, **params):
    extras = _pairs(params) if params else ""
    cmd = "{url}/command.cgi?op={op:d}{extras}".format(
        url=URL, op=op.value, extras=extras)
    return cmd.encode("UTF-8")


def _pairs(keyvals):
    pairs = "&".join("{}={}".format(key, val)
                     for key, val in keyvals.items())
    return "&" + pairs


##########################
# FlashAir API functions


def list_files(directory=DEFAULT_DIR):
    response = _cgi_cmd(Op.list_files, DIR=directory)
    return list(_split_file_list(response.text))


def count_files(directory=DEFAULT_DIR):
    response = _cgi_cmd(Op.count_files, DIR=directory)
    return int(response.text)


#############################
# API implementation details


def _cgi_cmd(op, **extras):
    cmd = make_cmd(op, **extras)
    logger.debug("Request: {}".format(cmd))
    response = requests.get(cmd)
    logger.debug("Response: {}".format(response))
    return response


_fields = ["directory", "filename", "size", "attribute", "date", "time"]
FileInfo = namedtuple("FileInfo", _fields)


def _split_file_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            yield FileInfo(*groups)


if __name__ == "__main__":
    print(list_files())
    print(count_files())

