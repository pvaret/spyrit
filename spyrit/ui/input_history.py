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

"""
Implements history for input boxes.
"""


from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QTextEdit

from spyrit.settings.spyrit_state import SpyritState


class Historian(QObject):
    """
    Provides logic to search up and down an input box's history.
    """

    _inputbox: QTextEdit
    _state: SpyritState.History

    _current_history: list[str] | None
    _current_index: int

    def __init__(
        self,
        inputbox: QTextEdit,
        state: SpyritState.History,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self._inputbox = inputbox
        self._state = state

        self._resetSearchState()

    @Slot(str)
    def recordNewInput(self, text: str) -> None:
        self._resetSearchState()

        if not text:
            return

        if (
            len(history := self._state.history) > 0
            and history[-1].get() == text
        ):
            return

        history.appendOne().set(text)
        extra_entries = len(history) - self._state.max_history_length.get()
        if extra_entries > 0:
            del history[:extra_entries]

    def _resetSearchState(self) -> None:
        self._current_history = None
        self._current_index = 0

    def _initializeSearchState(self) -> None:
        if self._current_history is not None:
            return

        self._current_history = [entry.get() for entry in self._state.history]
        self._current_history.append("")  # This will be filled when we move.
        self._current_history.reverse()

    def historyMove(self, delta: int) -> None:
        self._initializeSearchState()

        if (history := self._current_history) is None:
            return

        if not 0 <= self._current_index + delta < len(history):
            return

        # Store the potentially currently modified input at the position where
        # it was previously found.

        history[self._current_index] = self._inputbox.toPlainText()

        # And replace the input box's content with the historical content at the
        # next index.

        self._current_index += delta
        self._inputbox.clear()
        self._inputbox.append(history[self._current_index])

    @Slot()
    def historyNext(self) -> None:
        self.historyMove(-1)

    @Slot()
    def historyPrevious(self) -> None:
        self.historyMove(+1)
