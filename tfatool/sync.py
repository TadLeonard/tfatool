
import logging
import time
from pathlib import PosixPath, Path
import requests
from . import cgi
from .cgi import URL, DEFAULT_DIR


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def by_new_arrivals(*filters, remote_dir=DEFAULT_DIR, dest="."):
    old_files = set()
    while True:
        new_files = set(cgi.list_files(*filters, remote_dir=remote_dir))
        if old_files and old_files < new_files:
            new_arrivals = new_files - old_files
            logger.info("Files to sync:\n{}".format(
                "\n".join("  " + f.filename for f in new_arrivals)))
            for f in new_arrivals:
                _sync_file(dest, f)
        old_files = new_files
        time.sleep(1)


def by_time(*filters, remote_dir=DEFAULT_DIR, dest=".", count=1):
    files = cgi.list_files(*filters, remote_dir=remote_dir)
    most_recent = sorted(files, key=lambda f: (f.date, f.time))
    to_sync = most_recent[-count:]
    logger.info("Files to sync:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    for f in to_sync[::-1]:
        _sync_file(dest, f)


def by_name(*filters, remote_dir=DEFAULT_DIR, dest=".", count=1):
    files = cgi.list_files(*filters, remote_dir=remote_dir)
    greatest = sorted(files, key=lambda f: f.filename)
    to_sync = greatest[-count:]
    logger.info("Files to sync:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    for f in to_sync[::-1]:
        _sync_file(dest, f)


def _sync_file(destination_dir, fileinfo):
    local_path = Path(destination_dir, fileinfo.filename)
    if local_path.exists():
        logger.info("File '{}' already exists; not syncing from SD card".format(
                    str(local_path)))
    else:
        remote_path = PosixPath(fileinfo.directory, fileinfo.filename)
        logger.info("Copying remote file {} to {}".format(
                    str(remote_path), str(local_path)))
        streaming_file = _get_file(fileinfo)
        _write_file(str(local_path), streaming_file)


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
            for chunk in response.iter_content(1024):
                written += len(chunk)
                outfile.write(chunk)
    else:
        raise requests.RequestException("Expected status code 200")

