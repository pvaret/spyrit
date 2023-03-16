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
    REQUIRED_PYTHON_VERSION = constants.REQUIRED_PYTHON_VERSION
    REQUIRED_QT_VERSION = constants.REQUIRED_QT_VERSION

    def __init__(self):
        self.dependencies_met: bool = True
        self.python_check_msg: str = ""
        self.pyside_check_msg: str = ""
        self.qt_check_msg: str = ""

    def dependenciesMet(self) -> bool:
        self.checkPythonVersion()
        self.checkPySide6Installed()
        self.checkQtVersion()

        return self.dependencies_met

    def messages(self) -> Iterator[str]:
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
        v = sys.version_info[0:2]

        if v >= self.REQUIRED_PYTHON_VERSION:
            self.python_check_msg = "🗸 Found Python v%s.%s." % v

        else:
            self.dependencies_met = False
            self.python_check_msg = (
                "❌ Python v%d.%d required!" % self.REQUIRED_PYTHON_VERSION
            )

    def checkPySide6Installed(self) -> None:
        if PySide6 is None:
            self.dependencies_met = False
            self.pyside_check_msg = (
                "❌ PySide6 required!"
                " See https://pypi.org/project/PySide6/ for installation."
            )

        else:
            self.pyside_check_msg = "🗸 Found PySide6 v%s." % PySide6.__version__

    @staticmethod
    def qtVersion() -> tuple[bool, tuple[int, int]]:
        if QtCore is None:
            return False, (0, 0)

        # Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).
        version_str = str(QtCore.qVersion())
        version_numbers = [int(c) for c in version_str.split(".")]
        version = version_numbers[0], version_numbers[1]

        return True, version

    def checkQtVersion(self) -> None:
        found, version = self.qtVersion()

        if found and version >= self.REQUIRED_QT_VERSION:
            self.qt_check_msg = "🗸 Found Qt v%s.%s." % version[0:2]

        else:
            self.dependencies_met = False
            self.qt_check_msg = (
                "❌ Qt v%d.%d required!"
                " Installing the most recent version of PySide6"
                " (see https://pypi.org/project/PySide6/)"
                " should provide this dependency." % self.REQUIRED_QT_VERSION
            )
