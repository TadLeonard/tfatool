# tfatool

Tools for managing files with the Toshiba FlashAir wireless SD card.
See [FlashAir API documentation](https://flashair-developers.com/en/documents/api/) for more information. Features include:

* functions for easy usage of FlashAir's [command.cgi](https://flashair-developers.com/en/documents/api/commandcgi/)
* functions to facilitate copying/syncing files from FlashAir
* a command line tool for syncing FlashAir files with a local directory
<img align="right" src="_docs/flashair.jpg">

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

## Using the `tfatool` library
### Example 1: using FlashAir CGI commands
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

### Example 2: using file syncronization functions

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

```python
from tfatool import sync

# Sync forever
sync.by_new_arrivals(dest="/home/tad/Pictures/new")

# Sync only .raw files (forever) that are smaller than 3 MB
is_raw = lambda f: f.filename.lower.endswith(".raw", ".cr2")
is_small = lambda f: f.size < 3e6
sync.by_new_arrivals(is_raw, is_small, dest="/home/tad/Pictures/raw")
```

# Installation
Requires `requests` and `python3.4+`. Install with `pip3 install tfatool`.
