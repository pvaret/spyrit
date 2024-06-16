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
Implements the autocompletion feature for input boxes.
"""

import bisect
import logging
import threading
import zlib

from collections.abc import Sequence
from typing import overload

from PySide6.QtCore import (
    QEvent,
    QObject,
    QStringListModel,
    Qt,
    Slot,
)
from PySide6.QtGui import QKeyEvent, QTextCursor
from PySide6.QtWidgets import QCompleter, QPlainTextEdit, QTextEdit

from sunset import Key

from spyrit.resources.file import _Resource  # type: ignore
from spyrit.resources.file import ResourceFile
from spyrit.resources.resources import Misc
from spyrit.settings.key_shortcut import Shortcut
from spyrit.ui.action_with_key_setting import ActionWithKeySetting


def _sort_key(string: str) -> str:
    """
    Normalizes strings for sorting and lookup.

    Args:
        string: A string to be sorted or compared.

    Returns:
        The string, normalized.
    """
    return string.lower()


class StaticWordList(Sequence[str]):
    """
    Stores a static list of words, read from a gzip'ed resource file, sorted,
    and shared across instances of this class.

    Membership tests are O(1) and case-insensitive.

    Args:
        resource: The resource file name from which to read the compressed list
            of strings.
    """

    # These are *class* attributes. The static word list is shared between
    # instances of this class.
    _words: list[str] = []
    _wordset: set[str] = set()
    _lock: threading.Lock = threading.Lock()

    def __init__(self, resource: _Resource = Misc.WORDLIST_TXT_GZ) -> None:
        self._ensureWordListLoaded(resource)

    @classmethod
    def _ensureWordListLoaded(cls, resource: _Resource) -> None:
        """
        Loads the word list from the compressed resource file with the given
        name, if and only if it hasn't already been loaded by another instance
        of this class.

        Args:
            resource: The resource file name from which to read the compressed
                list of strings.
        """

        with cls._lock:
            if cls._words:
                return

            logging.debug("Loading auto-completion static word list...")
            compressed_data = ResourceFile(resource).readall()

            # This wbits parameter corresponds to gzip-compressed data.
            data = zlib.decompress(compressed_data, wbits=zlib.MAX_WBITS | 16)

            lines = data.decode("utf-8", errors="strict").splitlines()
            lines.sort(key=_sort_key)

            cls._words = lines
            cls._wordset = set(map(_sort_key, lines))

            logging.debug("Done loading auto-completion static word list.")

    def __len__(self) -> int:
        return StaticWordList._words.__len__()

    @overload
    def __getitem__(self, index: int) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> list[str]: ...

    def __getitem__(self, index: int | slice) -> str | list[str]:
        return StaticWordList._words[index]

    def __contains__(self, value: object) -> bool:
        return (
            isinstance(value, str)
            and _sort_key(value) in StaticWordList._wordset
        )

    @classmethod
    def reset(cls) -> None:
        """
        Clears the word list. For testing purposes.
        """

        with cls._lock:
            cls._words.clear()
            cls._wordset.clear()


class CompletionModel:
    """
    Holds the source of truth for existing completion candidates, and performs
    the matching for a given prefix.

    Args:
        static_word_list: A sequence of strings, assumed sorted, in which to look
            up matches by prefix.
    """

    # The minimal length of a match prefix, below which we don't look for matches.

    _MINIMUM_PREFIX_LEN = 3

    _words: Sequence[str]

    def __init__(self, static_word_list: Sequence[str] | None = None) -> None:
        if static_word_list is None:
            static_word_list = StaticWordList()
        self._words = static_word_list

    def findMatches(self, prefix: str) -> Sequence[str]:
        """
        Returns the list of known words that match the given prefix, in order.

        Args:
            prefix: The lookup prefix for which to find matches. If it's too
                short (currently less than 3 characters) no matches are returned.

        Returns:
            A sequence of words from the word list starting with the given prefix.
        """

        prefix = _sort_key(prefix)
        if len(prefix) < self._MINIMUM_PREFIX_LEN:
            return []

        index_left = bisect.bisect_left(self._words, prefix, key=_sort_key)
        index_right = index_left

        while index_right < len(self._words) and _sort_key(
            self._words[index_right]
        ).startswith(prefix):
            index_right += 1

        return self._words[index_left:index_right]


class Autocompleter(QCompleter):
    """
    Implements the UI of the autocompletion function.

    Args:
        widget: The text edit in which to perform autocompletion.

        model: The completion model in which to look up completion matches.

        shortcut: The key shortcut that invokes completion.
    """

    _widget: QTextEdit | QPlainTextEdit
    _model: CompletionModel
    _completion_cursor: QTextCursor

    def __init__(
        self,
        widget: QTextEdit | QPlainTextEdit,
        model: CompletionModel,
        shortcut: Key[Shortcut],
    ) -> None:
        super().__init__(parent=widget)

        self._widget = widget
        self._model = model
        self._completion_cursor = QTextCursor()

        self.setCompletionMode(
            QCompleter.CompletionMode.UnfilteredPopupCompletion
        )
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModelSorting(
            QCompleter.ModelSorting.CaseInsensitivelySortedModel
        )

        self.setWidget(widget)
        widget.installEventFilter(self)

        completion_action = ActionWithKeySetting(
            self,
            "Trigger autocompletion",
            shortcut,
            self.startCompletion,
        )
        widget.addAction(completion_action)

        self.activated.connect(self.applyCompletion)

    @Slot(str)
    def applyCompletion(self, text: str) -> None:
        """
        Inserts the given text over the text that served as the completion
        prefix.

        Args:
            text: The string to paste over the prefix used for completion.
        """

        if text and not self._completion_cursor.isNull():
            self._completion_cursor.insertText(text)
            self._completion_cursor.clearSelection()

    @Slot()
    def startCompletion(self) -> None:
        """
        Initiates the completion process.
        """

        self._completion_cursor = QTextCursor(self._widget.textCursor())

        if not self._completion_cursor.hasSelection():
            # TODO: Use a better selection algorithm, that accounts for words
            # that legitimately contain punctuation such as apostrophes.
            self._completion_cursor.select(
                QTextCursor.SelectionType.WordUnderCursor
            )

        prefix = self._completion_cursor.selectedText()

        if not prefix:
            return

        matches = self._model.findMatches(prefix)

        if not matches:
            return

        if len(matches) == 1:
            # If exactly one match was found, activate the completion without
            # showing the menu.

            self.activated.emit(matches[0])
            return

        self.setModel(QStringListModel(matches))

        # This causes Qt to fill and display the completion popup. From there
        # our custom event handler below can take over.

        self.complete()

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        """
        The default implementation of QCompleter intercepts some key events to
        route them to the popup, but not all. Because we do our own key event
        handling in our input boxes, we need to be explicit about which keys are
        considered part of the completion process.
        """

        if (popup := self.popup()) is None or not popup.isVisible():  # type: ignore
            return super().eventFilter(o, e)

        if o is not self._widget and o is not popup:
            return super().eventFilter(o, e)

        match e:
            case QKeyEvent() if e.type() == QKeyEvent.Type.ShortcutOverride:
                # Silently consume all shortcuts when the popup is visible.

                e.accept()
                return True

            case QKeyEvent() if e.type() == QKeyEvent.Type.KeyPress:
                # Up, down, page up and page down are passed verbatim to the popup.

                if (
                    e.modifiers() == Qt.KeyboardModifier.NoModifier
                    and e.key()
                    in (
                        Qt.Key.Key_Up,
                        Qt.Key.Key_Down,
                        Qt.Key.Key_PageUp,
                        Qt.Key.Key_PageDown,
                    )
                ):
                    return super().eventFilter(o, e)

                # Space, Enter, Return and Tab accept the current selection, if
                # any, and are then consumed without further processing.

                if (
                    e.modifiers() == Qt.KeyboardModifier.NoModifier
                    and e.key()
                    in (
                        Qt.Key.Key_Space,
                        Qt.Key.Key_Enter,
                        Qt.Key.Key_Return,
                        Qt.Key.Key_Tab,
                    )
                ):
                    index = popup.currentIndex()
                    if index.isValid():
                        txt = popup.model().data(index)
                        if txt:
                            self.activated.emit(txt)

                    popup.hide()
                    e.accept()
                    return True

                # All other cases end the completion process and let the event
                # fall through.

                popup.hide()

            case _:
                pass

        return super().eventFilter(o, e)
