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
Declaration of the Spyrit state "settings".
"""

import operator

from PySide6.QtCore import QSize
from sunset import Bunch, Key, Settings

from spyrit import constants
from spyrit.settings.serializers import IntList, Size

_default_size = QSize(
    constants.DEFAULT_WINDOW_WIDTH,
    constants.DEFAULT_WINDOW_HEIGHT,
)


def _size_validator(size: QSize) -> bool:
    return size.isValid() and not size.isEmpty()


class ToggleKey(Key[bool]):
    def toggle(self) -> None:
        self.updateValue(operator.not_)


class SpyritState(Settings):
    class UI(Bunch):
        window_size = Key(
            _default_size, serializer=Size(), validator=_size_validator
        )

        splitter_sizes = Key(default=[1000, 100, 100], serializer=IntList())
        second_input_visible = ToggleKey(default=False)

    ui = UI()

    def getStateSectionForSettingsSection(
        self, settings: Settings
    ) -> "SpyritState":
        hierarchy: list[str] = []

        while (parent := settings.parent()) is not None:
            hierarchy.append(settings.sectionName())
            settings = parent

        # Go up the state tree to find the root.

        state = self
        while (parent := state.parent()) is not None:
            state = parent

        # Return the state section equivalent to the given settings section.

        while hierarchy:
            state = state.getOrCreateSection(hierarchy.pop())

        return state
