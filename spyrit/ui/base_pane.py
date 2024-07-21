# Copyright (c) 2007-2024 Pascal Varet <p.varet@gmail.com>
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
Implements a base class that provides the common functionality between panes
contained in a SlidingPaneContainer.
"""


from PySide6.QtWidgets import QWidget


class Pane(QWidget):
    """
    Base class for widget that go into a SlidingPaneContainer.
    """

    # Whether the Pane will be garbage-collected when out of view.

    pane_is_persistent: bool = False

    def onActive(self) -> None:
        """
        This method is called by the pane container when this pane becomes
        active. Override in subclasses that need to take action when that
        happens.
        """
