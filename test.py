import os
import arrow

from urllib import parse
from tfatool.info import Config, WifiMode, DriveMode
from tfatool.config import config
from tfatool import command, upload


def test_config_construction():
    params = {Config.wifi_ssid: "chiquita"}
    cfg = config(params)
    assert cfg == {"MASTERCODE": "BEEFBEEFBEEF", "APPSSID": "chiquita"}


def test_invalid_timeout_value():
    params = {Config.wifi_timeout: 15}  # 15 secs is too short
    try:
        assert config(params)["APPAUTOTIME"] == 15000
    except AssertionError:
        pass
    else:
        assert False, "expected failed assertion"


def test_valid_timeout_value():
    params = {Config.wifi_timeout: 120.5201}
    assert config(params)["APPAUTOTIME"] == 120520
    

def test_full_config():
    params = {Config.wifi_timeout: 60,
              Config.app_info: "some info is fun",
              Config.wifi_mode: WifiMode.station,
              Config.wifi_key: "supersecret",
              Config.wifi_ssid: "chiquita",
              Config.passthrough_key: "verysecret",
              Config.passthrough_ssid: "officewifi",
              Config.bootscreen_path: "/DCIM/img.jpg",
              Config.mastercode: "BEEFBEEFBEEF",
              Config.clear_mastercode: ...,
              Config.timezone: -5,
              Config.drive_mode: DriveMode.disable,
             }
    assert config(params) == {
                'APPSSID': 'chiquita', 'CIPATH': '/DCIM/img.jpg',
                'BRGNETWORKKEY': 'verysecret', 'WEBDAV': 0,
                'APPINFO': 'some info is fun', 'APPAUTOTIME': 60000,
                'APPMODE': 2, 'APPNETWORKKEY': 'supersecret', 'TIMEZONE': -20,
                'BRGSSID': 'officewifi', 'CLEARCODE': 1,
                'MASTERCODE': 'BEEFBEEFBEEF'}
    

def test_command_cgi_query():
    req = command._prep_get(command.Operation.list_files, DIR="/DCIM/WOMP")
    _, query = parse.splitquery(req.url)
    query_map = parse.parse_qs(query)
    assert query_map == {"DIR": ["/DCIM/WOMP"], "op": ["100"]}


def test_command_cgi_url():
    req = command._prep_get(command.Operation.list_files, DIR="/DCIM/WOMP",
                            url="http://192.168.0.1")
    print(req.url)
    url, _ = parse.splitquery(req.url)
    assert url == "http://192.168.0.1/command.cgi"


def test_datetime_encode_decode():
    ctime = os.stat("README.md").st_ctime
    dtime = arrow.get(ctime)

    # encode to FAT32 time
    encoded = upload._encode_time(ctime)

    # decode to arrow datetime
    decoded = command._decode_time(encoded >> 16, encoded & 0xFFFF)

    # accurate down to the second
    for attr in "year month day hour minute second".split():
        assert getattr(dtime, attr) == getattr(decoded, attr)

