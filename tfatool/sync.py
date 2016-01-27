import logging
import os
import time

from pathlib import Path, PosixPath
from urllib.parse import urljoin

import arrow
import requests
import tqdm

from . import command, upload
from .info import URL, DEFAULT_REMOTE_DIR
from .info import RawFileInfo, SimpleFileInfo


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



######################################################
# Synchronizing in the DOWN (from FlashAir) direction

def down_by_arrival(*filters, remote_dir=DEFAULT_REMOTE_DIR, local_dir="."):
    """Monitor `remote_dir` on FlashAir card for new files.
    When new files are found, should they pass all of the given
    `filters`, sync them with `local_dir` local directory."""
    logger.info("Building remote file list")
    old_files = set(command.list_files(*filters, remote_dir=remote_dir))
    command.memory_changed()  # clear change status to start
    _notify_sync_ready(old_files)
    while True:
        if command.memory_changed():
            new_files = set(command.list_files(*filters, remote_dir=remote_dir))
            new_arrivals = new_files - old_files
            logger.info("Files to download:\n{}".format(
                "\n".join("  " + f.filename for f in new_arrivals)))
            by_files(new_arrivals, local_dir=local_dir)
            old_files = new_files
            _notify_sync_ready(old_files)
        time.sleep(0.3)


def down_by_files(to_sync, local_dir="."):
    """Sync a given list of files from `command.list_files` to `local_dir` dir"""
    for f in to_sync:
        _sync_remote_file(local_dir, f)


def down_by_time(*filters, remote_dir=DEFAULT_REMOTE_DIR, local_dir=".", count=1):
    """Sync most recent file by date, time attribues"""
    files = command.list_files(*filters, remote_dir=remote_dir)
    most_recent = sorted(files, key=lambda f: f.datetime)
    to_sync = most_recent[-count:]
    logger.info("Files to download:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    by_files(to_sync[::-1], local_dir=local_dir)


def down_by_name(*filters, remote_dir=DEFAULT_REMOTE_DIR, local_dir=".", count=1):
    """Sync files whose filename attribute is highest in alphanumeric order"""
    files = command.list_files(*filters, remote_dir=remote_dir)
    greatest = sorted(files, key=lambda f: f.filename)
    to_sync = greatest[-count:]
    logger.info("Files to download:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    by_files(to_sync[::-1], local_dir=local_dir)


def _sync_remote_file(local_dir, remote_file_info):
    local = Path(local_dir, remote_file_info.filename)
    local_name = str(local)
    remote_size = remote_file_info.size
    if local.exists():
        local_size = local.stat().st_size
        if local.stat().st_size == remote_size:
            logger.info(
                "Skipping '{}': already exists locally".format(
                local_name))
        else:
            logger.warning(
                "Removing {}: local size {} != remote size {}".format(
                local_name, local_size, remote_size))
            os.remove(local_name)
            _stream_to_file(local_name, remote_file_info)
    else:
        _stream_to_file(local_name, remote_file_info)


def _stream_to_file(local_name, fileinfo):
    logger.info("Copying remote file {} to {}".format(
                fileinfo.path, local_name))
    streaming_file = _get_file(fileinfo)
    _write_file_safely(local_name, fileinfo, streaming_file)


def _get_file(fileinfo):
    url = urljoin(URL, fileinfo.path)
    logger.info("Requesting file: {}".format(url)) 
    return requests.get(url, stream=True)


def _write_file_safely(local_path, fileinfo, response):
    """attempts to stream a remote file into a local file object,
    removes the local file if it's interrupted by any error"""
    try:
        _write_file(local_path, fileinfo, response)
    except BaseException as e:
        logger.warning("{} interrupted writing {} -- "
                       "cleaning up partial file".format(
                       e.__class__.__name__, local_path))
        os.remove(local_path)
        raise e


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


##################################################
# Synchronizing in the UP direction (to FlashAir)

def up_by_arrival(*filters, local_dir=".", remote_dir=DEFAULT_REMOTE_DIR):
    old_files = set(list_local_files(*filters, local_dir=local_dir))
    _notify_sync_ready(old_files)
    while True:
        new_files = set(list_local_files(*filters, local_dir=local_dir))
        if new_files > old_files: 
            new_arrivals = new_files - old_files
            logger.info("Files to upload:\n{}".format(
                "\n".join("  " + f.filename for f in new_arrivals)))
            up_by_files(new_arrivals, remote_dir)
            old_files = new_files
            _notify_sync_ready(old_files)
        time.sleep(0.3)


def up_by_files(to_sync, remote_dir=DEFAULT_REMOTE_DIR, remote_files=None):
    """Sync a given list of local files to `remote_dir` dir"""
    if remote_files is None:
        remote_files = command.map_files_raw(remote_dir=remote_dir)
    for local_file in to_sync:
        _sync_local_file(local_file, remote_dir, remote_files)


def up_by_time(*filters, local_dir=".", remote_dir=DEFAULT_REMOTE_DIR, count=1):
    """Sync most recent file by date, time attribues"""
    remote_files = command.map_files_raw(remote_dir=remote_dir)
    local_files = list_local_files(*filters, local_dir=local_dir)
    most_recent = sorted(local_files, key=lambda f: f.datetime)
    to_sync = most_recent[-count:]
    logger.info("Files to upload:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    up_by_files(to_sync[::-1], remote_dir, remote_files)


def up_by_name(*filters, local_dir=".", remote_dir=DEFAULT_REMOTE_DIR, count=1):
    """Sync files whose filename attribute is highest in alphanumeric order"""
    remote_files = command.map_files_raw(remote_dir=remote_dir)
    local_files = list_local_files(*filters, local_dir=local_dir)
    greatest = sorted(local_files, key=lambda f: f.filename)
    to_sync = greatest[-count:]
    logger.info("Files to upload:\n{}".format(
        "\n".join("  " + f.filename for f in to_sync)))
    up_by_files(to_sync[::-1], local_dir, remote_files)


def _sync_local_file(local_file_info, remote_dir, remote_files):
    local_name = local_file_info.filename
    local_size = local_file_info.size
    if local_name in remote_files:
        remote_file_info = remote_files[local_name]
        remote_size = remote_file_info.size
        if local_size == remote_size:
            logger.info(
                "Skipping '{}' already exists on SD card".format(
                local_name))
        else:
            logger.warning(
                "Removing remote file {}: "
                "local size {} != remote size {}".format(
                local_name, local_size, remote_size))
            upload.delete_file(remote_file_info.path)
            _stream_from_file(local_file_info, remote_dir)
    else:
        _stream_from_file(local_file_info, remote_dir)


def _stream_from_file(fileinfo, remote_dir):
    logger.info("Uploading local file {} to {}".format(
                fileinfo.path, remote_dir))
    _upload_file_safely(fileinfo, remote_dir)


def _upload_file_safely(fileinfo, remote_dir):
    """attempts to upload a local file to FlashAir,
    tries to remove the remote file if interrupted by any error"""
    try:
        upload.upload_file(fileinfo.path, remote_dir=remote_dir)
    except BaseException as e:
        logger.warning("{} interrupted writing {} -- "
                       "cleaning up partial remote file".format(
                       e.__class__.__name__, fileinfo.path))
        upload.delete_file(fileinfo.path)
        raise e


def list_local_files(*filters, local_dir="."):
    all_entries = os.scandir(local_dir)
    file_entries = (e for e in all_entries if e.is_file())
    for entry in file_entries:
        stat = entry.stat()
        size = stat.st_size
        datetime = arrow.get(stat.st_mtime)
        path = str(Path(local_dir, entry.name))
        info = SimpleFileInfo(local_dir, entry.name, path, size, datetime)
        if all(filt(info) for filt in filters):
            yield info


def list_local_files_raw(*filters, local_dir="."):
    all_entries = os.scandir(local_dir)
    all_files = (e for e in all_entries if e.is_file() and
                 all(filt(e) for filt in filters))
    for entry in all_files:
        path = str(Path(local_dir, entry.name))
        yield RawFileInfo(local_dir, entry.name, path, entry.stat().st_size)


 
def _notify_sync_ready(old_files):
    logger.info("Ready to sync new files ({:d} existing files ignored)".format(
                len(old_files)))


