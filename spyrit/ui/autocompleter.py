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
import enum
import logging
import threading
import zlib

from collections.abc import Iterable, Iterator, Sequence
from typing import overload

from PySide6.QtCore import (
    QEvent,
    QObject,
    QStringListModel,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QKeyEvent, QTextCursor
from PySide6.QtWidgets import QCompleter, QPlainTextEdit, QTextEdit

from sunset import Key

from spyrit.network.fragments import (
    FlowControlFragment,
    Fragment,
    NetworkFragment,
    TextFragment,
)
from spyrit.resources.file import _Resource  # type: ignore
from spyrit.resources.file import ResourceFile
from spyrit.resources.resources import Misc
from spyrit.settings.key_shortcut import Shortcut
from spyrit.ui.action_with_key_setting import ActionWithKeySetting


class Case(enum.Enum):
    UNSPECIFIED = enum.auto()
    CAPITALIZED = enum.auto()
    ALL_CAPS = enum.auto()


def _compute_case(text: str) -> Case:
    """
    Determines the case of the given text using a simple heuristic.

    "TEXT" is ALL_CAPS.
    "Text" is CAPITALIZED.
    "text" is UNSPECIFIED.

    Args:
        text: The text whose case is to be determined.

    Returns:
        A best guess as to the text's case.
    """

    if not text:
        return Case.UNSPECIFIED

    # Special case: if the text is one letter only, we can't tell if the intent
    # is ALL_CAPS or CAPITALIZED. We arbitrarily pick CAPITALIZED.
    # Note: this assumes the text starts with a letter.

    if len(text) == 1:
        return Case.CAPITALIZED if text.isupper() else Case.UNSPECIFIED

    if text.isupper():
        return Case.ALL_CAPS

    if text[0].isupper():
        return Case.CAPITALIZED

    return Case.UNSPECIFIED


def _apply_case(case: Case, text: str) -> str:
    """
    Applies the given case to the given text.

    UNSPECIFIED leaves the text unmodified.
    CAPITALIZED turns e.g. "banana" into "Banana".
    ALL_CAPS turns e.g. "banana" into "BANANA".

    Args:
        case: The case to be applied to the text.

        text: The text whose case is to be updated.

    Returns:
        The input text, with its case updated.
    """

    match case:
        case Case.UNSPECIFIED:
            return text
        case Case.ALL_CAPS:
            return text.upper()
        case Case.CAPITALIZED:
            return text[0].upper() + text[1:]


def _sort_key(string: str) -> str:
    """
    Normalizes strings for sorting and lookup.

    Args:
        string: A string to be sorted or compared.

    Returns:
        The string, normalized.
    """
    return string.casefold()


class CaseInsensitiveSet(set[str]):
    def add(self, element: str) -> None:
        return super().add(_sort_key(element))

    def update(self, *s: Iterable[str]) -> None:
        for iterable in s:
            super().update(map(_sort_key, iterable))

    def remove(self, element: str) -> None:
        return super().remove(_sort_key(element))

    def __contains__(self, o: object) -> bool:
        return isinstance(o, str) and super().__contains__(_sort_key(o))


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
    _word_set: set[str] = CaseInsensitiveSet()
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
            cls._word_set.update(lines)

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
        return value in StaticWordList._word_set

    @classmethod
    def reset(cls) -> None:
        """
        Clears the word list. For testing purposes.
        """

        with cls._lock:
            cls._words.clear()
            cls._word_set.clear()


class Tokenizer(QObject):
    """
    Consumes a Fragment stream from a world and extracts text tokens.

    Args:
        parent: The QObject to attach this object to for lifetime management
            purposes.
    """

    # This signal is emitted whenever the tokenizer has found a complete token
    # in its input.

    tokenFound: Signal = Signal(str)

    _text_so_far: str

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._text_so_far = ""

    def processFragments(self, fragments: Iterable[Fragment]) -> None:
        """
        Ingests the given Fragment stream and emits the tokenFound signal for
        each valid text token found.

        Args:
            fragments: A stream of fragments coming from a world.
        """

        for fragment in fragments:
            match fragment:
                case TextFragment(text):
                    self._text_so_far += text

                case FlowControlFragment() | NetworkFragment():
                    if self._text_so_far:
                        for token in self._tokenize(self._text_so_far):
                            self.tokenFound.emit(token)
                        self._text_so_far = ""

                case _:
                    pass

    def _tokenize(self, text: str) -> Iterator[str]:
        """
        A dumb tokenizer function that extracts tokens made of letters and
        apostrophes only. The apostrophes must be inside the word, and
        surrounded by letters.

        Args:
            text: The string to extract tokens from.

        Returns:
            An iterator over the found tokens.
        """

        word = ""
        for c in text:
            if c.isalpha():
                word += c
                continue

            if c == "'" and word and word[-1] != "'":
                word += c
                continue

            if word := word.strip("'"):
                yield word
                word = ""

        if word := word.strip("'"):
            yield word


class CompletionModel(QObject):
    """
    Holds the source of truth for existing completion candidates, and performs
    the matching for a given prefix.

    Args:
        static_word_list: A sequence of strings, assumed sorted, in which to look
            up matches by prefix.

        parent: The QObject to attach this object to for lifetime management
            purposes.
    """

    # The minimal length of a match prefix, below which we don't look for matches.

    _MINIMUM_PREFIX_LEN = 3

    _static_words: Sequence[str]
    _extra_words: list[str]
    _extra_word_set: set[str]

    def __init__(
        self,
        static_word_list: Sequence[str] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        if static_word_list is None:
            static_word_list = StaticWordList()
        self._static_words = static_word_list
        self._extra_words = []
        self._extra_word_set = CaseInsensitiveSet()

    @Slot(str)
    def addExtraWord(self, word: str) -> None:
        """
        Records a new word into the completion model.

        If the word is (case-insensitively) already present in the static word
        list or in the extra word list, it will be skipped.

        Args:
            word: The word to be considered for addition to the model.
        """

        if word not in self._static_words and word not in self._extra_word_set:
            bisect.insort_left(self._extra_words, word, key=_sort_key)
            self._extra_word_set.add(word)

    def findMatches(self, prefix: str) -> Sequence[str]:
        """
        Returns the list of known words that match the given prefix, in order.

        If the prefix is capitalized or all-caps, the matches will
        correspondingly be capitalized or turned to all-caps.

        Args:
            prefix: The lookup prefix for which to find matches. If it's too
                short (currently less than 3 characters) no matches are returned.

        Returns:
            A sequence of words from the word list starting with the given prefix.
        """

        prefix_case = _compute_case(prefix)
        prefix = _sort_key(prefix)

        matches: list[str] = []

        if len(prefix) < self._MINIMUM_PREFIX_LEN:
            return matches

        for source in (self._static_words, self._extra_words):
            index_left = bisect.bisect_left(source, prefix, key=_sort_key)
            index_right = index_left

            while index_right < len(source) and _sort_key(
                source[index_right]
            ).startswith(prefix):
                index_right += 1

            for match in source[index_left:index_right]:
                bisect.insort_left(
                    matches, _apply_case(prefix_case, match), key=_sort_key
                )

        return matches


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
