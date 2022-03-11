# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

#
# Win32Specific.py
#
# Contains the class that implements Windows-specific elements.
#


import os.path

from typing import cast

import winpaths


class Win32Specific:

    CONFIG_DIR = "Spyrit"
    OLD_CONFIG_DIRS = []
    CONFIG_FILE = "Spyrit.ini"
    STATE_FILE = "spyrit.state"

    should_repaint_on_scroll = False
    default_font = "Courier New"

    def get_homedir(self):
        return winpaths.get_homedir()

    def get_settings_dir(self):
        appdata = cast(str, winpaths.get_appdata())
        return os.path.join(appdata, self.CONFIG_DIR)

    def get_old_settings_dirs(self):
        appdata = cast(str, winpaths.get_appdata())
        return [os.path.join(appdata, dir) for dir in self.OLD_CONFIG_DIRS]

    def get_settings_file(self):
        return os.path.join(self.get_settings_dir(), self.CONFIG_FILE)

    def get_state_file(self):
        return os.path.join(self.get_settings_dir(), self.STATE_FILE)

    def get_sound_backends(self):
        return ["qsound"]
