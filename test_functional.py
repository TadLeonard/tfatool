import logging
logging.basicConfig(level=logging.DEBUG, style="{",
                    format="{asctime} | {levelname} | {name} | {message}")
from tfatool import command, upload


fns = [
    lambda: list(command.list_files())[:5],
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

upload.upload_file("README.md", dest="/DCIM")
upload.delete_file("/DCIM/README.md")


for fn in fns:
    val = fn()
    print("\n\n*** Command {}:\n{} (type: {})".format(
          fn.__name__, val, type(val)))

