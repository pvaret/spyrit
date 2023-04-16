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
Implements a base class that provides the common functionality between panes
contained in a SlidingPaneContainer.
"""


from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class Pane(QWidget):
    """
    Base class for widget that go into a SlidingPaneContainer.
    """

    # This signal is sent when the SlidingPaneContainer makes this pane active.

    active = Signal()  # noqa: N815

    # This signal is sent when the SlidingPaneContainer makes this pane
    # inactive.

    inactive = Signal()  # noqa: N815

    def makeActive(self) -> None:
        self.setEnabled(True)
        self.active.emit()

    def makeInactive(self) -> None:
        self.setEnabled(False)
        self.inactive.emit()
