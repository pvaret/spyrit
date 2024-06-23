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
Implements logic to automatically log into games after connection.
"""

import logging

from collections.abc import Sequence
from typing import Any, Callable

from PySide6.QtCore import QObject, Slot

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    Fragment,
    FragmentList,
    NetworkFragment,
    TextFragment,
)
from spyrit.settings.scrambled_text import ScrambledText
from spyrit.settings.spyrit_settings import LoginStyle, SpyritSettings


def _get_login_string(
    name: str, password: ScrambledText, login_style: LoginStyle
) -> str:
    """
    Assembles and returns the string to send to the world to log in a character.

    Args:
        name: The character's name.

        password: The character's password, scrambled,

        login_style: What login format is expected by the game.

    Returns:
        The login string, ready to send to the game. An empty string if any of
        the parameters are empty.
    """

    if name and password:
        match login_style:
            case LoginStyle.CONNECT_NAME_PASSWORD_CR:
                return f"connect {name} {password.plaintext()}\n"

    return ""


class Autologin(QObject):
    """
    Implements automatically sending a login string when connecting to a world.

    Args:
        settings: The Settings login object that contains the parameters to be
            used for computing the login string.

        send: A callable to be used to send login strings to the game world.

        parent: A QObject to use as this object's parent. Used for lifetime
            management.
    """

    _settings: SpyritSettings.Login
    _send: Callable[[str], Any]
    _login_sent: bool
    _connected: bool

    def __init__(
        self,
        settings: SpyritSettings.Login,
        send: Callable[[str], Any],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self._settings = settings
        self._send = send
        self._login_sent = False
        self._connected = False

    @Slot(FragmentList)
    def awaitLoginPrecondition(self, fragments: Sequence[Fragment]) -> None:
        """
        Scans the given fragments to determine when to send the login string.

        Args:
            fragments: A sequence of fragments as produced by the game's
                fragment processor.
        """

        if not (name := self._settings.name.get()) or not (
            password := self._settings.password.get()
        ):
            return

        for fragment in fragments:
            match fragment:
                case NetworkFragment(event=Status.CONNECTED):
                    self._connected = True
                    self._login_sent = False

                case NetworkFragment(event=Status.DISCONNECTED):
                    self._connected = False

                case TextFragment() if self._connected and not self._login_sent:
                    # We only send a login string after the game has sent some
                    # text. This avoids a theoretical race condition where the
                    # game would have accepted the connection, but not yet fired
                    # up its login function.

                    self._sendLogin(
                        name, password, self._settings.login_style.get()
                    )
                    self._login_sent = True

                case _:
                    pass

    def _sendLogin(
        self, name: str, password: ScrambledText, login_style: LoginStyle
    ) -> None:
        """
        Creates a login string and sends it to the game world, using the send
        function provided on instantiation.

        Args:
            name: The name of the character to log in.

            password: The password of the character to log in, scrambled.

            login_style: Which format to use for the login string.
        """

        if login_string := _get_login_string(name, password, login_style):
            logging.debug(f"Sending login string for '{name}'.")
            self._send(login_string)
