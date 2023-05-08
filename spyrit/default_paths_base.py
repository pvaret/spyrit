# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
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

import pathlib

from abc import ABC, abstractmethod

from spyrit import constants


class DefaultPathsBase(ABC):
    PID_FILE_NAME = constants.PID_FILE_NAME

    _config_folder_path: pathlib.Path | None

    def __init__(self) -> None:
        self._config_folder_path = None

        super().__init__()

    @abstractmethod
    def getConfigFileName(self) -> str:
        ...

    @abstractmethod
    def getStateFileName(self) -> str:
        ...

    @abstractmethod
    def getDefaultConfigFolder(self) -> pathlib.Path:
        ...

    def getUserHomeFolder(self) -> pathlib.Path:
        return pathlib.Path.home()

    def setConfigFolderPath(self, path: str) -> None:
        self._config_folder_path = pathlib.Path(path)

    def getConfigFolderPath(self) -> pathlib.Path:
        if self._config_folder_path:
            config_folder_path = self._config_folder_path

        else:
            config_folder_path = self.getDefaultConfigFolder()

        return config_folder_path.absolute().resolve()

    def getConfigFilePath(self) -> pathlib.Path:
        return self.getConfigFolderPath() / self.getConfigFileName()

    def getStateFilePath(self) -> pathlib.Path:
        return self.getConfigFolderPath() / self.getStateFileName()

    def getPidFilePath(self) -> pathlib.Path:
        return self.getConfigFolderPath() / self.PID_FILE_NAME
