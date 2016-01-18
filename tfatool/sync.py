
import logging
from pathlib import PosixPath, Path
import requests
from . import cgi
from .cgi import URL, DEFAULT_DIR


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def sync_most_recent_file(*filters, remote_dir=DEFAULT_DIR, dest="."):
    files = cgi.list_files(directory, *filters)
    most_recent = max(files, key=lambda f: (f.date, f.time))
    logger.debug("Most recent file: {}".format(most_recent))
    _sync_file(dest, most_recent)
    

def sync_greatest_named_file(*filters, remote_dir=DEFAULT_DIR, dest="."):
    files = cgi.list_files(directory, *filters)
    greatest = max(files, key=lambda f: f.filename)
    logger.debug("Greatest filename alphabetically: {}".format(greatest))
    _sync_file(dest, greatest)


def _sync_file(destination_dir, fileinfo):
    local_path = Path(destination_dir, fileinfo.filename)
    if local_path.exists():
        logger.info("File '{}' already exists; not syncing from SD card".format(
                    str(local_path)))
    else:
        remote_path = PosixPath(fileinfo.directory, fileinfo.filename)
        logger.info("Copying remote file {:s} to {:s}".format(
                    remote_path, local_path))
        streaming_file = _get_file(fileinfo)
        _write_file(local_path, streaming_file)


def _get_file(fileinfo):
    path = PosixPath(fileinfo.directory, fileinfo.filename)
    flashair_url = (URL + str(path)).encode("UTF-8")
    logger.debug("Requesting file: {}".format(flashair_url)) 
    request = requests.get(flashair_url, stream=True)
    return request


def _write_file(local_path, response):
    if response.status_code == 200:
        written = 0
        with open(local_path, "wb") as outfile:
            for chunk in response.iter_response(1024):
                written += len(chunk)
                outfile.write(chunk)
                print("Bytes written: {:d}\r".format(written))
            print()
    else:
        raise requests.RequestException("Expected status code 200")

