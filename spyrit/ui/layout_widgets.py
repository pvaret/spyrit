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
Implements widgets to help lay out a UI.
"""

from typing import cast

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QBoxLayout,
    QHBoxLayout,
    QLayout,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from sunset import Key

from spyrit.ui.sizer import Sizer


class Box(QWidget):
    """
    Helper class to contain widgets in a given layout.

    Args:
        layout: The layout to use for adding widgets in this box.
    """

    def __init__(self, layout: QLayout) -> None:
        super().__init__()

        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def addWidget(self, widget: QWidget) -> None:
        """
        Adds a widget to this box's layout.

        Args:
            widget: The widget to add.
        """

        self.layout().addWidget(widget)

    def layout(self) -> QBoxLayout:
        """
        Returns the layout used for the widgets in this box.

        Returns:
            The layout, properly typed.
        """

        return cast(QBoxLayout, super().layout())


class VBox(Box):
    """
    Helper class to lay out widgets vertically.
    """

    def __init__(self) -> None:
        super().__init__(QVBoxLayout())


class HBox(Box):
    """
    Helper class to lay out widgets vertically.
    """

    def __init__(self) -> None:
        super().__init__(QHBoxLayout())


class Splitter(QSplitter):
    """
    A specialized splitter that saves its status in settings.

    Args:
        sizes: The settings key to use to save the splitter's sizes.

        widgets: The list of widgets to add to this splitter, in order.
    """

    _sizes: Key[list[int]]

    def __init__(self, sizes: Key[list[int]], *widgets: QWidget) -> None:
        super().__init__()

        self._sizes = sizes

        self.setChildrenCollapsible(False)
        self.setOrientation(Qt.Orientation.Vertical)
        self.setHandleWidth(Sizer(self).marginSize())

        for widget in widgets:
            self.addWidget(widget)

        self.setSizes(sizes.get())

        self.splitterMoved.connect(self._saveSplitterSizes)

    @Slot()
    def _saveSplitterSizes(self) -> None:
        """
        Saves the splitter's status to the splitter's setting object.
        """

        self._sizes.set(self.sizes())
