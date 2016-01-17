import requests
from collections import namedtuple
from enum import Enum


URL = "http://flashair"
DIR = "/DCIM"


class Op(Enum):
    list_files = 100


def make_cmd(op, **params):
    extras = _pairs(params) if params else ""
    cmd = "{url}/command.cgi?op={op:d}{extras}".format(
        url=URL, op=op.value, extras=extras)
    return cmd


def _pairs(keyvals):
    pairs = "&".join("{}={}".format(key, val)
                     for key, val in keyvals.items())
    return "&" + pairs


def list_images(directory="/DCIM/100__TSB"):
    cmd = make_cmd(Op.list_files, DIR="/DCIM/100__TSB")
    response = requests.get(cmd)
    return list(_split_img_list(response.text))


info_params = ["directory", "filename", "size", "attribute",
               "date", "time"]
FileInfo = namedtuple("FileInfo", info_params)


def _split_img_list(text):
    lines = text.split("\r\n")
    for line in lines:
        groups = line.split(",")
        if len(groups) == 6:
            yield FileInfo(*groups)


def count_images(directory="/DCIM/100__TSB"):
    pass


if __name__ == "__main__":
    print(list_images())
