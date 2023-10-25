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
Implements app-specific buttons.
"""

from textwrap import TextWrapper

from PySide6.QtWidgets import QPushButton

from spyrit.settings.spyrit_settings import SpyritSettings

# TODO: make this a function of the font size.
_UNIT = 16
_WORLD_BUTTON_WRAP = 30


def linewrap(text: str) -> str:
    wrapper = TextWrapper()
    wrapper.width = _WORLD_BUTTON_WRAP

    return "\n".join(wrapper.wrap(text))


class Button(QPushButton):
    def __init__(self, label: str) -> None:
        super().__init__(label)

        self.setStyleSheet(f"padding: {_UNIT/1.5} {_UNIT} {_UNIT/1.5} {_UNIT}")


class WorldButton(Button):
    _settings: SpyritSettings

    def __init__(self, settings: SpyritSettings) -> None:
        self._settings = settings

        label = settings.name.get() or "(Unnamed)"

        super().__init__(linewrap(label))

    def settings(self) -> SpyritSettings:
        return self._settings
