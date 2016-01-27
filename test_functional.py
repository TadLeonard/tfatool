import logging
logging.basicConfig(level=logging.DEBUG, style="{",
                    format="{asctime} | {levelname} | {name} | {message}")
from tfatool import command, upload


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
    upload.upload_file("README.md", dest="/DCIM")
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

