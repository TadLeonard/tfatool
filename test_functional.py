import logging
import os
import threading
import time
logging.basicConfig(level=logging.DEBUG, style="{",
                    format="{asctime} | {levelname} | {name} | {message}")
from tfatool import command, upload, sync


fns = [
    command.count_files,
    command.memory_changed,
    command.get_ssid,
    command.get_password,
    command.get_mac,
    command.get_browser_lang,
    command.get_fw_version,
    command.get_ctrl_image,
    command.get_wifi_mode,
    
]


def test_upload_delete():
    upload.delete_file("/DCIM/README.md")
    files = command.list_files(remote_dir="/DCIM")
    assert not any(f.filename == "README.md" for f in files)
    upload.upload_file("README.md", remote_dir="/DCIM")
    files = command.list_files(remote_dir="/DCIM")
    assert any(f.filename == "README.md" for f in files)
    upload.delete_file("/DCIM/README.md")
    assert not any(f.filename == "README.md" for f in files)


def test_list_files():
    files = command.list_files()
    raw_files = command.list_files()
    same_attrs = "filename directory size".split()
    for n, (f, r) in enumerate(zip(files, raw_files)):
        assert all(getattr(f, n) == getattr(r, n) for n in same_attrs)
    assert n > 3, "too few files to test"


def test_smoke():
    """Smoke test: just runs every command.cgi function"""
    for fn in fns:
        val = fn()
        print("\n\n*** Command {}:\n{} (type: {})".format(
              fn.__name__, val, type(val)))


def _prepare_test_files(local_only=False):
    test_names = ["__testfile{0}".format(n) for n in range(2, -1, -1)]
    name_filter = lambda f: f.filename.startswith("__testfile")
    for f in test_names:
        os.system("touch {}".format(f))
        if not local_only:
            upload.delete_file("/DCIM/{}".format(f))
    return test_names, name_filter


def _teardown_test_files(names):
    for name in names:
        try:
            os.remove(name)
        except OSError:
            pass


def test_watch_local():
    watcher = sync.watch_local_files()
    new_files, all_files = next(watcher)
    assert not new_files
    names, name_filter = _prepare_test_files(local_only=True)
    new_files, all_files = next(watcher)
    assert {f.filename for f in new_files} == set(names)
    new_files, all_files = next(watcher)
    assert not new_files
    _teardown_test_files(names)


def test_sync_up_by_time():
    names, name_filter = _prepare_test_files()
    sync.up_by_time(name_filter, remote_dir="/DCIM", count=1)
    files = command.list_files(name_filter, remote_dir="/DCIM")
    files = list(files)
    assert len(files) == 1
    assert files[0].path == "/DCIM/__testfile0"
    upload.delete_file(files[0].path)
    _teardown_test_files(names)
 

def test_sync_up_by_name():
    names, name_filter = _prepare_test_files() 
    sync.up_by_name(name_filter, remote_dir="/DCIM", count=2)
    files = command.list_files(name_filter, remote_dir="/DCIM")
    files = list(files)
    assert len(files) == 2
    assert [f.filename for f in files] == ["__testfile2", "__testfile1"]
    for f in files:
        upload.delete_file(f.path)
    _teardown_test_files(names)


def test_sync_up_by_arrival_threaded():
    names, name_filter = _prepare_test_files() 
    _teardown_test_files(names)

    monitor = sync.Monitor(name_filter, remote_dir="/DCIM")
    monitor.sync_up()
    time.sleep(0.2)
    _prepare_test_files()  # files get `touch`ed
    time.sleep(2)
    monitor.stop()
    files = list(command.list_files(name_filter, remote_dir="/DCIM")) 

    for f in files:
        upload.delete_file(f.path) 
    _teardown_test_files(names)

    assert len(files) == len(names)

def test_sync_up_by_arrival():
    names, name_filter = _prepare_test_files()
    _teardown_test_files(names)

    to_upload = sync.up_by_arrival(name_filter, remote_dir="/DCIM")
    _, new = next(to_upload)  # nothing new yet
    assert not new  # empty set
    _prepare_test_files()  # files get `touch`ed
    _, new = next(to_upload)  # should be something new to upload
    assert len(new) == len(names)
    _, new = next(to_upload)  # triggers upload, then yields an empty set again
    assert not new
    files = list(command.list_files(name_filter, remote_dir="/DCIM"))

    for f in files:
        upload.delete_file(f.path)
    _teardown_test_files(names)

    assert len(files) == len(names)

