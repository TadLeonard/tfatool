import logging
from enum import Enum
from . import cgi
from .info import URL


class Param(str, Enum):
    timeout = "APPAUTOTIME"  # set connection timeout
    info = "APPINFO"  # set "application unique info"
    mode = "APPMODE"  # set WLAN mode (see Mode and ModeOnBoot)
    key = "APPNETWORKKEY"  # set network security key
    ssid = "APPSSID"  # set SSID
    passthrough_key = "BRGNETWORKKEY"  # set internet passthrough sec. key
    passthrough_ssid = "BRGSSID"  # set internet passthrough SSID
    bootscreen_path = "CIPATH"  # set wireless LAN bootscreen path
    clear_mastercode = "CLEARCODE"  # clear mastercode
    timezone = "TIMEZONE"  # set timezone (e.g. 36)
    flashair_drive = "WEBDAV"  # set FlashAir drive (WebDAV)
    

class ModeValue(int, Enum): ...
 

class Mode(ModeValue):
    """Wireless modes effective IMMEDIATELY"""
    access_point = 0
    station = 2
    passthrough = 3  # for wireless pass through (FW 2.00.02+)


class ModeOnBoot(ModeValue): 
    """Wireless modes effective upon REBOOT of the device"""
    access_point = 4
    station = 5
    passthrough = 6


def post(url=URL, **params):
    for param_key in params:
        if param_key not in Param:
            raise ValueError("Config parameter {} is invalid".format(
                             param_key))
    
    

