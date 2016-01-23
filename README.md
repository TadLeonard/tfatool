# tfatool

This package provides easy access to the features of
Toshiba's FlashAir wireless SD card. As a library, this project provides
a simple abstraction of the FlashAir API. As a set of scripts, `tfatool`
gives the user a way of synchronizing files and configuring the device
from the command line.

<img align="right" src="_docs/flashair.jpg">

Features include:

* `flashair-util`: a command line tool for managing files on FlashAir (syncing/copying files, listing files, etc.)
* `flashair-config`: a command line tool for configuring FlashAir
* `tfatool.command`: abstraction of FlashAir's [command.cgi](https://flashair-developers.com/en/documents/api/commandcgi/)
* `tfatool.config`: abstraction of FlashAir's [config.cgi](https://flashair-developers.com/en/documents/api/configcgi/)
* `tfatool.sync`: functions to facilitate copying/syncing files from FlashAir

See [FlashAir API documentation](https://flashair-developers.com/en/documents/api/)
for more information about the FlashAir API `tfatool` takes advantage of.

# Usage
## Using the `flashair-util` script
### Help menu
```
$ flashair-util -h
usage: flashair-util [-h] [-r REMOTE_DIR] [-d LOCAL_DIR] [-l] [-c] [-s]
                     [-S {timestamp,name}] [-n N_FILES] [-j] [-k MATCH_REGEX]

optional arguments:
  -h, --help            show this help message and exit
  -r REMOTE_DIR, --remote-dir REMOTE_DIR
  -d LOCAL_DIR, --local-dir LOCAL_DIR
  -l, --list-files
  -c, --count-files
  -s, --sync-forever
  -S {timestamp,name}, --sync-once {timestamp,name}
  -n N_FILES, --n-files N_FILES
  -j, --only-jpg
  -k MATCH_REGEX, --match-regex MATCH_REGEX
                        filter for files that match the given pattern
```

### Example 1: sync newly created files on FlashAir card
Watch for new files on the FlashAir SD card. When new files are found,
write them to a specified directory.

```
$ flashair-util -s -d path/to/images 
INFO:__main__:Syncing files from /DCIM/100__TSB to path/to/images
INFO:__main__:Waiting for newly arrived files...
INFO:tfatool.sync:Files to sync:
  IMG_0672.CR2
  IMG_0672.JPG
INFO:tfatool.sync:Copying remote file /DCIM/100__TSB/IMG_0672.CR2 to path/to/images/IMG_0672.CR2
```


### Example 2: list all JPEG files on FlashAir device
```
$ flashair-util --list-files --only-jpg

Files in /DCIM/100__TSB
=======================
FA000001.JPG
IMG_0152.JPG
IMG_0153.JPG
...
IMG_0325.JPG
(179 files)
```

`flashair-util -l -j` and `flashair-util -l -k '.+\.JPG'` are equivalent.

## Using the `flashair-config` script
### Help menu
```
flashair-config -h
usage: flashair-config [-h] [-m MASTERCODE] [-v] [-t WIFI_TIMEOUT]
                       [-w {access_point,station,passthrough}] [-W]
                       [-k WIFI_KEY] [-K PASSTHROUGH_KEY] [-s WIFI_SSID]
                       [-S PASSTHROUGH_SSID] [--app-info APP_INFO]
                       [--bootscreen-path BOOTSCREEN_PATH] [-M]
                       [--timezone TIMEZONE] [-d {disable,enable,upload}]

optional arguments:
  -h, --help            show this help message and exit
  -m MASTERCODE, --mastercode MASTERCODE
                        12-digit hex mastercode to enable configuration of the
                        FlashAir device
  -v, --verbose

WiFi settings:
  -t WIFI_TIMEOUT, --wifi-timeout WIFI_TIMEOUT
                        set WiFi timeout of device
  -w {access_point,station,passthrough}, --wifi-mode {access_point,station,passthrough}
                        set WiFi mode of device
  -W, --wifi-mode-on-boot
                        set the WiFi mode on next boot, not immediately
  -k WIFI_KEY, --wifi-key WIFI_KEY
                        set WiFi security key
  -K PASSTHROUGH_KEY, --passthrough-key PASSTHROUGH_KEY
                        set internet passthrough security key
  -s WIFI_SSID, --wifi-ssid WIFI_SSID
                        set WiFi SSID
  -S PASSTHROUGH_SSID, --passthrough-ssid PASSTHROUGH_SSID
                        set internet passthrough SSID

Misc settings:
  --app-info APP_INFO   set application-specific info
  --bootscreen-path BOOTSCREEN_PATH
                        set path to boot screen image
  -M, --clear-mastercode
  --timezone TIMEZONE   set timezone in hours offset (e.g. -8)
  -d {disable,enable,upload}, --drive-mode {disable,enable,upload}
                        set WebDAV drive mode
```

### Sample configurations of FlashAir

Set the FlashAir WiFi network's SSID and password.

```flashair-config -k supersecretekey -s myflashairnetwork```

Prepare for Internet passthrough mode. This sets the LAN SSID, password, and
the FlashAir WiFi mode. If this is successful, the device will pass through
Internet access to all connected clients.

```flashair-config -K supersecretekey -S coffeeshopssid -w passthrough```

Set the WiFi mode *on boot* instead of immediately with the *-W* flag:

```flashair-config -w station -W```


## Using the `tfatool` Python library
### Example 1: using FlashAir's command.cgi

```python
from tfatool import command

def list_and_count_files():
  flashair_files = command.list_files()  # list files in /DCIM/100__TSB by default
  n_flashair_files = command.count_files(DIR="/DCIM")  # count in specific directory
  special_files = command.list_files(DIR="/DCIM/my_special_folder")

  
def examine_large_files():
  # the list_files CGI command provides six interesting file attributes
  for f in command.list_files():
    if f.filename.lower().endswith(".raw", ".cr2"):
      continue  # skip raw files
    if size > 10**7:
      # file size greater than 10 MB!
      print("Huge file ({:d} bytes): {}/{} created on {}-{}".format(
            f.size, f.directory, f.filename, f.date, f.time))
    print(f.time, f.date)  # time and date encoded as integers
```

### Example 2: using file synchronization functions

```python
from tfatool import sync

# Sync files as a one-off action
sync.by_timestamp(count=10)  # places most recent files in CWD by default
sync.by_timestamp(count=15, dest="/home/tad/Pictures")

# Sync specific files selected from list_files
from tfatool import command
all_files = command.list_files()
only_camille_photos = [f for f in all_files if "camille" in f.filename.lower()]
sync.by_files(only_camille_photos, dest="/home/tad/Pictures/camille")
```

### Example 3: using new file monitoring function
The `tfatool.sync.by_new_arrivals()` function watches your FlashAir device
for new files. When new files are found, they're copied to the local directory
specified by the `dest` argument (current working directory by default).


### Example 4: watching for newly created files

```python
from tfatool import sync

# Monitor FlashAir for new files, sync them with a local directory
# This will run forever
sync.by_new_arrivals(dest="/home/tad/Pictures/new")

# Sync only .raw image files that are smaller than 3 MB
# This will run forever
is_raw = lambda f: f.filename.lower().endswith(".raw", ".cr2")
is_small = lambda f: f.size < 3e6
sync.by_new_arrivals(is_raw, is_small, dest="/home/tad/Pictures/raw")
```

### Example 5: sending config changes via a POST to *config.cgi*

```python
from tratool.config import config, Param, post

params = {
    Param.app_info: "special application info",
    Param.wifi_timeout: 3600,  # one-hour WiFi timeout
    Param.wifi_ssid: "SUPER FUN PHOTO ZONE",
    Param.timezone: -11,  # somewhere in the USA, for example
}

# This will raise an assertion error if any parameters are invalid
# or out of range (for example if the WiFi timeout is < 60 seconds)
prepped_params = config(params)

# Prompt reconfiguration of the device via an HTTP POST to config.cgi
response = post(prepped_params)
if response.status_code == 200:
    print("FlashAir reconfiguration successful")
else:
    print("Error: {}".format(response.status_code))
```

# Installation
Requires `requests`, `tqdm`, and `python3.4+`. Install with `pip3 install tfatool`.
