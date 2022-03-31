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

"""
Provides a base class for platform-specific path lookup object. To be overriden
platform by platform.
"""

import os
import pathlib

from abc import ABC, abstractmethod


class DefaultPathsBase(ABC):
    def __init__(self) -> None:

        super().__init__()

        self.config_folder_path = ""

    @abstractmethod
    def getConfigFileName(self) -> str:
        ...

    @abstractmethod
    def getDefaultConfigFolder(self) -> str:
        ...

    def getUserHomeFolder(self) -> str:

        return str(pathlib.Path.home())

    def setConfigFolderPath(self, path: str) -> None:

        self.config_folder_path = path

    def getConfigFolderPath(self) -> str:

        if self.config_folder_path:
            config_folder_path = self.config_folder_path

        else:
            config_folder_path = self.getDefaultConfigFolder()

        return os.path.abspath(config_folder_path)

    def getConfigFilePath(self) -> str:

        return os.path.join(
            self.getConfigFolderPath(), self.getConfigFileName()
        )
