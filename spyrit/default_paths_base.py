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
    """
    Base class for per-OS configuration path classes.
    """

    PID_FILE_NAME = constants.PID_FILE_NAME
    DEBUG_LOG_FILE_NAME = constants.DEBUG_LOG_FILE_NAME

    _config_folder_path: pathlib.Path | None = None

    @abstractmethod
    def getConfigFileName(self) -> str:
        """
        Returns the name of the configuration file to be used on this OS.

        Returns:
            A file name, without its path.
        """

    @abstractmethod
    def getStateFileName(self) -> str:
        """
        Returns the name of the state file to be used on this OS.

        Returns:
            A file name, without its path.
        """

    @abstractmethod
    def getDefaultConfigFolder(self) -> pathlib.Path:
        """
        Returns the path to the default folder to be used for configuration
        files. This is OS-dependant. The default folder is the folder that will
        be used if not explicitly overridden using setConfigFolderPath().

        Returns:
            The path to the default location where configuration files will be
            saved.
        """

    def getUserHomeFolder(self) -> pathlib.Path:
        """
        Returns the path to the user's home folder.

        Returns:
            A path.
        """
        return pathlib.Path.home()

    def setConfigFolderPath(self, path: str) -> None:
        """
        Updates the configuration folder path.

        Args:
            path: The path to the folder that will now be used to store
                configuration files.
        """

        self._config_folder_path = pathlib.Path(path)

    def getConfigFolderPath(self) -> pathlib.Path:
        """
        Returns the path to the currently set configuration folder if any, or
        the OS-dependant default for the current user.

        Returns:
            A path to the current configuration folder.
        """

        if self._config_folder_path:
            config_folder_path = self._config_folder_path

        else:
            config_folder_path = self.getDefaultConfigFolder()

        return config_folder_path.absolute().resolve()

    def getConfigFilePath(self) -> pathlib.Path:
        """
        Returns the full path to the configuration file, using the configured
        configuration folder if any.

        Returns:
            The full path to the configuration file.
        """

        return self.getConfigFolderPath() / self.getConfigFileName()

    def getStateFilePath(self) -> pathlib.Path:
        """
        Returns the full path to the state file, using the configured
        configuration folder if any.

        Returns:
            The full path to the state file.
        """

        return self.getConfigFolderPath() / self.getStateFileName()

    def getPidFilePath(self) -> pathlib.Path:
        """
        Returns the full path to the PID file, using the configured
        configuration folder if any.

        Returns:
            The full path to the PID file.
        """

        return self.getConfigFolderPath() / self.PID_FILE_NAME

    def getDebugLogFilePath(self) -> pathlib.Path:
        """
        Returns the full path to the debug log file, using the configured
        configuration folder if any.

        Returns:
            The full path to the debug log file.
        """

        return self.getConfigFolderPath() / self.DEBUG_LOG_FILE_NAME
