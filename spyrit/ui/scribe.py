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
Implements a class that translates network fragments into text and formatting to
be applied to a cursor.
"""


import logging

from typing import Iterable

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QTextCursor

from spyrit.network.connection import Status
from spyrit.network.fragments import (
    Fragment,
    FragmentList,
    NetworkFragment,
    TextFragment,
)


class Scribe(QObject):
    """
    A class that receives a stream of processed fragments and expresses it as
    formatted text on the given cursor.
    """

    _cursor: QTextCursor

    def __init__(
        self, cursor: QTextCursor, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)

        self._cursor = cursor

    @Slot(FragmentList)
    def inscribe(self, fragments: Iterable[Fragment]) -> None:
        """
        Expresses the given fragments as formatted text on this Scribe's cursor.
        """

        for fragment in fragments:
            match fragment:
                case TextFragment(text):
                    self._cursor.insertText(text)

                case NetworkFragment(event, text):
                    match event:
                        case Status.DISCONNECTED:
                            message = "Disconnected."
                        case Status.RESOLVING:
                            message = f"Looking up '{text}'..."
                        case Status.CONNECTING:
                            message = "Connecting..."
                        case Status.CONNECTED:
                            message = "Connected!"
                        case Status.ERROR:
                            message = f"Error: {text}!"
                    self._insertStatusText(message)

                case _:
                    logging.debug(
                        "Unexpected fragment type in Scribe: '%s'",
                        fragment.__class__.__name__,
                    )

    def _insertStatusText(self, text: str) -> None:
        self._cursor.insertText(f"→ {text}\n")
