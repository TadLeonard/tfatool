import logging
import requests
from functools import partial
from enum import Enum
from urllib.parse import urljoin
from .info import URL


logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)


class Entrypoint(str, Enum):
    command = "command.cgi"
    config = "config.cgi"
    upload = "upload.cgi"
    thumbnail = "thumbnail.cgi"


def request(method, entrypoint, url=URL, **params):
    resource = urljoin(url, entrypoint)
    logger.debug("Request: {}".format(resource))
    response = requests.request(method, resource, params=params)
    logger.debug("Response: {}".format(response))
    return response


get = partial(request, "GET")
post = partial(request, "POST")

