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
Implements a key shortcut type that's serializable by SunsetSettings.
"""

from typing import Optional

from PySide6 import QtGui


class KeyShortcut(QtGui.QKeySequence):
    """
    A subclass of QKeySequence that can be serialized into SunsetSettings.
    """

    @classmethod
    def fromStr(cls, value: str) -> Optional["KeyShortcut"]:
        """
        Build a KeyShortcut from native text. Native means that Cmd on Mac OS X
        typically takes the role of Ctrl on Linux/Windows.
        """

        key = KeyShortcut(
            value, format=QtGui.QKeySequence.SequenceFormat.NativeText
        )
        return None if key.isEmpty() else key

    def toStr(self) -> str:
        """
        Serialize a KeyShortcut to native text. Native means that Cmd on Mac OS
        X typically takes the role of Ctrl on Linux/Windows.
        """

        return self.toString(
            format=QtGui.QKeySequence.SequenceFormat.NativeText
        )


def from_default(value: str) -> KeyShortcut:
    """
    Build a KeyShortcut from *portable* text. Portable means that we can
    specify the same shortcut on all platforms and Qt adapts it to the
    native modifiers for the platform.
    """

    key = KeyShortcut(
        value, format=QtGui.QKeySequence.SequenceFormat.PortableText
    )
    return key
