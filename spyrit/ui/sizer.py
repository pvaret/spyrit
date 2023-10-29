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
Provides a helper class that computes UI element sizes.
"""

from PySide6.QtWidgets import QWidget

from spyrit import constants


class Sizer:
    """
    A helper class that computes the desired pixel size for various UI elements,
    accounting for HiDPI displays.

    Args:
        widget: The widget for which to compute sizes.
    """

    _widget: QWidget

    def __init__(self, widget: QWidget) -> None:
        self._widget = widget

    def _pixelRatio(self) -> float:
        """
        Computes the pixel ratio for this Sizer's widget.

        Returns:
            The pixel ratio for the widget this Sizer is attached to. Typically
            1.0, or 2.0 for HiDPI devices.
        """

        return self._widget.window().devicePixelRatio()

    def unitSize(self) -> int:
        """
        Returns the size of a standard UI block. Using a standard block size,
        and expressing widget sizes in terms of a number of these blocks, helps
        the UI look more harmonious.

        Returns:
            A size, in pixels.
        """

        return round(constants.UI_UNIT_SIZE_PX * self._pixelRatio())
