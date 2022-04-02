# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
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

#
# QTextEditWithClickableLinks.py
#
# This file contains the QTextEditWithClickableLinks class, which implements
# the same interaction between mouse and links as in QTextBrowser.
#


from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QDesktopServices


class QTextEditWithClickableLinks(QTextEdit):

    linkClicked = pyqtSignal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.previous_anchor = ""
        self.click_pos = QPoint()
        self.click_link = ""

        self.setMouseTracking(True)

        flags = self.textInteractionFlags()
        flags |= Qt.TextInteractionFlag.LinksAccessibleByMouse
        self.setTextInteractionFlags(flags)

        self.linkClicked.connect(self.onLinkClicked)

    def mouseMoveEvent(self, e):

        maybe_anchor = self.anchorAt(e.pos())

        if maybe_anchor != self.previous_anchor:

            if maybe_anchor:
                self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)

            else:
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

            self.previous_anchor = maybe_anchor

        return super().mouseMoveEvent(e)

    def mousePressEvent(self, e):

        self.click_pos = e.pos()
        self.click_link = self.anchorAt(e.pos())

        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):

        diff = QPoint(
            e.pos().x() - self.click_pos.x(), e.pos().y() - self.click_pos.y()
        )
        if diff.manhattanLength() <= 3:
            if self.click_link and self.click_link == self.anchorAt(e.pos()):
                self.linkClicked.emit(self.click_link)

        return super().mouseReleaseEvent(e)

    def onLinkClicked(self, href):

        QDesktopServices.openUrl(QUrl(href))
