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
Utility class that checks if the requisite dependencies are installed.
"""

import sys

from typing import Iterator

try:
    import PySide6
except (ModuleNotFoundError, ImportError):
    PySide6 = None  # type: ignore

try:
    from PySide6 import QtCore
except (ModuleNotFoundError, ImportError):
    QtCore = None  # type: ignore

from . import constants


# A command-line argument to be used when the program's dependencies should be
# checked but the program itself should not be run.
CHECK_DEPENDENCIES_ARG = "--check-dependencies-only"


class DependencyChecker:
    """
    A helper that can check if the application's required dependencies are
    installed.
    """

    REQUIRED_PYTHON_VERSION = constants.REQUIRED_PYTHON_VERSION
    REQUIRED_QT_VERSION = constants.REQUIRED_QT_VERSION

    def __init__(self) -> None:
        self.dependencies_met: bool = True
        self.python_check_msg: str = ""
        self.pyside_check_msg: str = ""
        self.qt_check_msg: str = ""

    def dependenciesMet(self) -> bool:
        """
        Checks whether all the needed dependencies are installed.

        Returns:
            Whether such is the case.
        """

        self.checkPythonVersion()
        self.checkPySide6Installed()
        self.checkQtVersion()

        return self.dependencies_met

    def messages(self) -> Iterator[str]:
        """
        Collects and returns the dependency check messages (be it successes or
        errors).

        Will not return anything useful if the checker functions have not been
        called yet.

        Returns:
            An iterator on the dependency check messages.
        """

        return (
            msg
            for msg in (
                self.python_check_msg,
                self.pyside_check_msg,
                self.qt_check_msg,
            )
            if msg
        )

    def checkPythonVersion(self) -> None:
        """
        Checks whether the required version of Python is installed, and records
        the result and a user-friendly explanation message.
        """

        v = sys.version_info[0:2]

        if v >= self.REQUIRED_PYTHON_VERSION:
            py_major, py_minor = v
            self.python_check_msg = f"🗸 Found Python v{py_major}.{py_minor}."

        else:
            self.dependencies_met = False
            py_major, py_minor = self.REQUIRED_PYTHON_VERSION
            self.python_check_msg = f"❌ Python v{py_major}.{py_minor} required!"

    def checkPySide6Installed(self) -> None:
        """
        Checks whether the required version of PySide6 is installed, and records
        the result and a user-friendly explanation message.
        """
        if PySide6 is None:
            self.dependencies_met = False
            self.pyside_check_msg = (
                "❌ PySide6 required!"
                " See https://pypi.org/project/PySide6/ for installation."
            )

        else:
            version = PySide6.__version__
            self.pyside_check_msg = f"🗸 Found PySide6 v{version}."

    @staticmethod
    def qtVersion() -> tuple[bool, tuple[int, int]]:
        """
        Computes and return the currently used version of Qt, if any, in a
        convenient programmatic format.

        Returns:
            A tuple of whether a suitable version was found, along with that
            version as a (major, minor) tuple.
        """
        if QtCore is None:
            return False, (0, 0)

        # Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).

        # WORKAROUND: qVersion() returns a string in recent PySide versions, but
        # is incorrectly typed as still returning bytes. Casting to str solves
        # the type variance and the typing issue both.

        version_str = str(QtCore.qVersion())
        version_numbers = [int(c) for c in version_str.split(".")]
        version = version_numbers[0], version_numbers[1]

        return True, version

    def checkQtVersion(self) -> None:
        """
        Checks whether the required version of Qt is installed, and records the
        result and a user-friendly explanation message.
        """

        found, version = self.qtVersion()

        if found and version >= self.REQUIRED_QT_VERSION:
            qt_major, qt_minor = version
            self.qt_check_msg = f"🗸 Found Qt v{qt_major}.{qt_minor}."

        else:
            self.dependencies_met = False
            qt_major, qt_minor = self.REQUIRED_QT_VERSION
            self.qt_check_msg = (
                f"❌ Qt v{qt_major}.{qt_minor} required!"
                " Installing the most recent version of PySide6"
                " (see https://pypi.org/project/PySide6/)"
                " should provide this dependency."
            )
