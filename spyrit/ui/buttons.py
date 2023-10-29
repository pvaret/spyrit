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

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.sizer import Sizer


def linewrap(
    text: str, line_length: int = constants.BUTTON_WRAP_CHARACTER
) -> str:
    """
    Wraps the given text to the given length.

    Args:
        text: The text to wrap.

        line_length: The length (in character counts) to which to wrap the text.

    Returns:
        The input text, wrapped.
    """

    wrapper = TextWrapper()
    wrapper.width = line_length

    return "\n".join(wrapper.wrap(text))


class Button(QPushButton):
    """
    A QPushButton with a standardized size.

    Args:
        label: The text to use for the button.
    """

    def __init__(self, label: str) -> None:
        super().__init__(label)

        unit = Sizer(self).unitSize()
        self.setStyleSheet(f"padding: {unit/1.5} {unit} {unit/1.5} {unit}")


class WorldButton(Button):
    """
    A button that is linked to the settings of a specific game world.

    Args:
        settings: The specific settings object for the game world linked to this
            button.
    """

    _settings: SpyritSettings

    def __init__(self, settings: SpyritSettings) -> None:
        self._settings = settings

        label = settings.name.get() or "(Unnamed)"

        super().__init__(linewrap(label))

    def settings(self) -> SpyritSettings:
        """
        Returns the settings object for the game world linked to this button.

        Returns:
            The settings object.
        """

        return self._settings
