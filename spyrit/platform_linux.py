# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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

"""
Implement platform-specific parameters for Linux.
"""

import pathlib

from spyrit import constants
from spyrit.default_paths_base import DefaultPathsBase


class DefaultPaths(DefaultPathsBase):
    CONFIG_FILE_NAME = constants.CONFIG_FILE_NAME_LINUX
    CONFIG_FOLDER_NAME = constants.CONFIG_FOLDER_NAME_LINUX

    def getConfigFileName(self) -> str:
        return self.CONFIG_FILE_NAME

    def getDefaultConfigFolder(self) -> pathlib.Path:
        return self.getUserHomeFolder() / self.CONFIG_FOLDER_NAME
