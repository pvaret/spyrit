# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## SettingsPaths.py
##
## Contains the code that figures out the paths used by this program depending
## on the OS.
##


import os.path

from PlatformSpecific import platformSpecific

SETTINGS_DIR = platformSpecific.get_settings_dir()
SETTINGS_FILE = platformSpecific.get_settings_file()
SETTINGS_FILE_CANDIDATES = [
    os.path.join(dir, platformSpecific.CONFIG_FILE)
    for dir in [SETTINGS_DIR] + platformSpecific.get_old_settings_dirs()
]
STATE_FILE = platformSpecific.get_state_file()
STATE_FILE_CANDIDATES = [
    os.path.join(dir, platformSpecific.STATE_FILE)
    for dir in [SETTINGS_DIR] + platformSpecific.get_old_settings_dirs()
]
LOG_DIR = os.path.join(SETTINGS_DIR, "logs")

FILE_ENCODING = "UTF-8"


if not os.path.exists(SETTINGS_DIR):

    try:
        os.makedirs(SETTINGS_DIR)

    except (IOError, OSError):
        pass
