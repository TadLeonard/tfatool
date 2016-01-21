from tfatool.config import config, Param, WifiMode, DriveMode


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
    params = {Param.wifi_timeout: 120}
    assert config(params)["APPAUTOTIME"] == 120000
    

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
            
    
