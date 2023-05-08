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
Provides a protocol that describes the UIRemote class.

This helps us avoid the introduction of an import cycle problem, since the
UIRemote implementation knows about the MainUI class, but the classes that use
the remote shouldn't.
"""

from typing import Callable, Protocol

from spyrit.ui.base_pane import Pane


class UIRemoteProtocol(Protocol):
    def append(self, pane: Pane) -> None:
        ...

    def pop(self) -> None:
        ...

    def setWindowTitle(self, title: str) -> None:
        ...

    def setTabTitle(self, title: str) -> None:
        ...

    def setCloseRequestCallback(self, callback: Callable[[], bool]) -> None:
        ...
