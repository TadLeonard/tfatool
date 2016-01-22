from urllib import parse
from tfatool.config import config, Param, WifiMode, DriveMode
from tfatool import command


def test_config_construction():
    params = {Param.wifi_ssid: "chiquita"}
    cfg = config(params)
    assert cfg == {"MASTERCODE": "BEEFBEEFBEEF", "APPSSID": "chiquita"}


def test_invalid_timeout_value():
    params = {Param.wifi_timeout: 15}  # 15 secs is too short
    try:
        assert config(params)["APPAUTOTIME"] == 15000
    except AssertionError:
        pass
    else:
        assert False, "expected failed assertion"


def test_valid_timeout_value():
    params = {Param.wifi_timeout: 120.5201}
    assert config(params)["APPAUTOTIME"] == 120520
    

def test_full_config():
    params = {Param.wifi_timeout: 60,
              Param.app_info: "some info is fun",
              Param.wifi_mode: WifiMode.station,
              Param.wifi_key: "supersecret",
              Param.wifi_ssid: "chiquita",
              Param.passthrough_key: "verysecret",
              Param.passthrough_ssid: "officewifi",
              Param.bootscreen_path: "/DCIM/img.jpg",
              Param.mastercode: "BEEFBEEFBEEF",
              Param.clear_mastercode: ...,
              Param.timezone: -5,
              Param.drive_mode: DriveMode.disable,
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

