import logging
from enum import Enum
from . import cgi
from .info import URL


class Param(str, Enum):
    wifi_timeout = "APPAUTOTIME"  # set wifi timeout
    app_info = "APPINFO"  # set "application unique info"
    wifi_mode = "APPMODE"  # set WLAN mode (see Mode and ModeOnBoot)
    wifi_key = "APPNETWORKKEY"  # set network security key
    wifi_ssid = "APPSSID"  # set SSID
    passthrough_key = "BRGNETWORKKEY"  # set internet passthrough sec. key
    passthrough_ssid = "BRGSSID"  # set internet passthrough SSID
    bootscreen_path = "CIPATH"  # set wireless LAN bootscreen path
    mastercode = "MASTERCODE"  # set mastercode (required!)
    clear_mastercode = "CLEARCODE"  # clear mastercode
    timezone = "TIMEZONE"  # set timezone (e.g. 36)
    drive_mode = "WEBDAV"  # set FlashAir drive (WebDAV)
    

class _ModeValue(int, Enum): ...
 

class WifiMode(_ModeValue):
    """Wireless modes effective IMMEDIATELY"""
    access_point = 0
    station = 2
    passthrough = 3  # for wireless pass through (FW 2.00.02+)


class WifiModeOnBoot(_ModeValue):
    """Wireless modes effective upon REBOOT of the device"""
    access_point = 4
    station = 5
    passthrough = 6


class DriveMode(_ModeValue):
    disable = 0  # FlashAir Drive disabled
    enable = 1  # enabled, only read is allowed
    # NOTE: for uploads to work, you also need UPLOAD=1 in the config file
    upload = 2  # enabled, read AND write allowed


def config(param_map, mastercode="BEEFBEEFBEEF"):
    pmap = {Param.mastercode: mastercode}
    pmap.update(param_map)
    processed_params = dict(_process_params(pmap))
    return processed_params


def _process_params(params):
    for param, value in params.items():
        assert param in Param, "Invalid param: {}".format(param)
        yield param.value, value_validators[param](value)


def post(param_map, url=URL):
    logger.info("Posting config params: {}".format(params)) 
    return cgi.post(url, params=param_map)


######################################################
# Functions for creating config POST parameter values


value_validators = {}


def _validator(parameter):
    def wrapper(fn):
        value_validators[parameter] = fn
        return fn
    return wrapper


@_validator(Param.wifi_timeout)
def _validate_timeout(seconds: float):
    """Creates an int from 60000 to 4294967294 that represents a
    valid millisecond wireless LAN timeout"""
    param_value = int(seconds * 1000)
    assert 60000 <= param_value <= 4294967294 
    return param_value


@_validator(Param.app_info)
def _validate_app_info(info: str):
    assert 1 <= len(info) <= 16
    return info


@_validator(Param.wifi_mode)
def _validate_wifi_mode(mode: _ModeValue):
    assert mode in WifiMode or mode in WifiModeOnBoot
    return int(mode) 


@_validator(Param.wifi_key)
def _validate_wifi_key(network_key: str):
    assert 0 <= len(network_key) <= 63
    return network_key


@_validator(Param.wifi_ssid)
def _validate_wifi_ssid(network_ssid: str):
    assert 1 <= len(network_ssid) <= 32
    return network_ssid


@_validator(Param.passthrough_key)
def _validate_passthrough_key(network_key: str):
    assert 0 <= len(network_key) <= 63
    return network_key


@_validator(Param.passthrough_ssid)
def _validate_passthroughssid(network_ssid: str):
    assert 1 <= len(network_ssid) <= 32
    return network_ssid


@_validator(Param.mastercode)
def _validate_mastercode(code: str):
    assert len(code) == 12
    code = code.upper()
    valid_chars = "0123456789ABCDEF"
    assert all(c in valid_chars for c in code)
    return code


@_validator(Param.bootscreen_path)
def _validate_bootscreen_path(path: str):
    return path


@_validator(Param.clear_mastercode)
def _validate_clear_mastercode(_):
    return 1


@_validator(Param.timezone)
def _validate_timezone(hours_offset: int):
    """Creates an int from -48 to 36 that represents the timezone
    offset in 15-minute increments as per the FlashAir docs"""
    param_value = int(hours_offset * 4)
    assert -48 <= param_value <= 36
    return param_value


@_validator(Param.drive_mode)
def _validate_drive_mode(mode: DriveMode):
    assert mode in DriveMode
    return int(mode)

