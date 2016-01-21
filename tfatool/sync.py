import logging
import time
from pathlib import Path, PosixPath
from urllib.parse import urljoin
import requests
import tqdm
from . import command
from .info import URL, DEFAULT_DIR


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def by_new_arrivals(*filters, remote_dir=DEFAULT_DIR, dest="."):
    """Monitor `remote_dir` on FlashAir card for new files.
    When new files are found, should they pass all of the given
    `filters`, sync them with `dest` local directory."""
    old_files = set(command.list_files(*filters, remote_dir=remote_dir))
    logger.info("Ready to sync new files ({:d} existing files ignored)".format(
                len(old_files)))
    while True:
        new_files = set(command.list_files(*filters, remote_dir=remote_dir))
        if old_files < new_files:
            new_arrivals = new_files - old_files
            logger.info("Files to sync:\n{}".format(
                "\n".join("  " + f.filename for f in new_arrivals)))
            for f in new_arrivals:
                _sync_file(dest, f)
        old_files = new_files
        time.sleep(1)


def by_files(to_sync, dest="."):
    """Sync a given list of files from `command.list_files` to `dest` dir"""
    for f in to_sync:
        _sync_file(dest, f)


def by_time(*filters, remote_dir=DEFAULT_DIR, dest=".", count=1):
    """Sync most recent file by date, time attribues"""
    files = command.list_files(*filters, remote_dir=remote_dir)
    most_recent = sorted(files, key=lambda f: (f.date, f.time))
    to_sync = most_recent[-count:]
    logger.info("Files to sync:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    for f in to_sync[::-1]:
        _sync_file(dest, f)


def by_name(*filters, remote_dir=DEFAULT_DIR, dest=".", count=1):
    """Sync files whose filename attribute is highest in alphanumeric order"""
    files = command.list_files(*filters, remote_dir=remote_dir)
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
        logger.info("Copying remote file {} to {}".format(
                    fileinfo.filename, str(local_path)))
        streaming_file = _get_file(fileinfo)
        _write_file(str(local_path), fileinfo, streaming_file)


def _get_file(fileinfo):
    url = URL + "/" + str(PosixPath(fileinfo.directory, fileinfo.filename))
    logger.info("Requesting file: {}".format(url)) 
    request = requests.get(url, stream=True)
    return request


def _write_file(local_path, fileinfo, response):
    start = time.time() 
    pbar_size = fileinfo.size / (5 * 10**5)
    pbar = tqdm.tqdm(total=int(pbar_size))
    if response.status_code == 200:
        with open(local_path, "wb") as outfile:
            for chunk in response.iter_content(5*10**5):
                progress = len(chunk) / (5 * 10**5)
                pbar.update(int(progress))
                outfile.write(chunk)
    else:
        raise requests.RequestException("Expected status code 200")
    pbar.close()
    duration = time.time() - start
    logger.info("Wrote {} in {:0.2f} s ({:0.2f} MB, {:0.2f} MB/s)".format(
                fileinfo.filename, duration, fileinfo.size / 10 ** 6,
                fileinfo.size / (duration * 10 ** 6)))

