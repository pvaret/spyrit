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
Implements a text search function.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QWidget,
)


class SearchBar(QWidget):
    """
    Provides a UI to perform searches in a text document.

    Search occurs from the bottom up by default, as that's more appropriate for
    our documents where the most recent text, and so most relevant, is at the
    bottom of the doc.

    Args:
        document: The document in which to perform searches.
    """

    # This signal fires when a search completed. The QTextCursor that's emitted
    # contains the found text as its selection, or a null cursor if there was no
    # or no further result.

    searchResultReady: Signal = Signal(QTextCursor)  # noqa: N815

    # This signal fires when this search bar no longer wants to have the focus.

    expelFocus: Signal = Signal()  # noqa: N815

    # This signal fires when the search bar becomes visible (True) or,
    # respectively, hidden (False).

    visibilityChanged: Signal = Signal(bool)  # noqa: N815

    _document: QTextDocument
    _search_cursor: QTextCursor
    _textbox: QLineEdit

    def __init__(self, document: QTextDocument) -> None:
        super().__init__()

        self._document = document
        self._search_cursor = QTextCursor()

        self.setLayout(QHBoxLayout())
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self.layout().setContentsMargins(4, 4, 4, 0)

        self.layout().addWidget(QLabel("Find:"))
        self.layout().addWidget(textbox := QLineEdit())
        self.layout().addWidget(search_up := QToolButton())
        self.layout().addWidget(search_down := QToolButton())

        search_up.setText("⏶")
        search_down.setText("⏷")

        search_up.setToolTip("Find previous")
        search_down.setToolTip("Find next")

        search_up.clicked.connect(self.findPrevious)
        search_down.clicked.connect(self.findNext)

        search_up.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        search_down.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._textbox = textbox
        self._textbox.returnPressed.connect(self.findPrevious)

        self.setFocusProxy(self._textbox)

    def show(self) -> None:
        """
        Makes this search bar visible and active.
        """

        super().show()
        self._textbox.setFocus()
        self.visibilityChanged.emit(True)

    def hide(self) -> None:
        """
        Makes this search bar invisible and expels its focus if it has it.
        """

        if self.hasFocus():
            self.expelFocus.emit()

        super().hide()
        self.visibilityChanged.emit(False)

        # When hiding the search bar, reset the search cursor position.

        self._search_cursor = QTextCursor()

    def toggle(self) -> None:
        """
        Hides or shows the search bar depending on its current status.
        """

        if self.isHidden():
            self.show()
        else:
            self.hide()

    def findPrevious(self) -> None:
        """
        Finds the next occurrence of the search text, moving upward.
        """

        # WORKAROUND: Backwards search does not work if the cursor is unset. So
        # we set it to the end of the document.
        if self._search_cursor.isNull():
            self._search_cursor = QTextCursor(self._document)
            self._search_cursor.movePosition(QTextCursor.MoveOperation.End)

        self._doSearch(QTextDocument.FindFlag.FindBackward)

    def findNext(self) -> None:
        """
        Finds the next occurrence of the search text, moving downward.
        """

        self._doSearch(QTextDocument.FindFlag(0))

    def _doSearch(self, flags: QTextDocument.FindFlag) -> None:
        """
        Performs the search of the text contained in the text edit over the
        document associated with this search bar.

        Args:
            flags: The behavior flags to use for the search.
        """

        text = self._textbox.text()

        if not text:
            return

        self._search_cursor = self._document.find(
            text, self._search_cursor, flags
        )
        self.searchResultReady.emit(self._search_cursor)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Overrides the default key handler to handle the Escape key explicitly.
        The Escape key closes the search bar.

        Args:
            event: The key event to handle.
        """

        if event.key() == Qt.Key.Key_Escape:
            self.hide()

        super().keyPressEvent(event)
