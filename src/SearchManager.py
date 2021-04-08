# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## SearchManager.py
##
## This file implements the SearchManager class, a helper that handles all
## aspects of searching the contents of a QTextEdit such as WorldOutputUI.
##


from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QTextDocument


class SearchManager:
    def __init__(self, textedit, settings):

        self.textedit = textedit
        self.settings = settings

        self.cursor = None
        self.previous_search = None

    def find(self, string=None):

        ## An empty search string means repeating the last search.

        if not string:
            string = self.previous_search

        ## Unless the last search was empty, in which case we bail out.

        if not string:
            return False

        ## Reset the search cursor if this is a new search.

        if string != self.previous_search:
            self.cursor = None

        cursor = self.cursor
        textedit = self.textedit
        document = textedit.document()

        self.previous_search = string

        ## Create new cursor at end of document if this is a new search.

        if not cursor:
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.End)

        cursor = document.find(string, cursor, QTextDocument.FindBackward)

        if cursor.isNull():  ## String was not found!

            ## Clear selection by setting an empty cursor, and scroll back to bottom
            ## of window.

            cursor = QTextCursor(document)
            textedit.setTextCursor(cursor)
            textedit.moveScrollbarToBottom()

            self.cursor = None

            return False

        else:

            textedit.setTextCursor(cursor)
            textedit.ensureCursorVisible()

            self.cursor = cursor

            return True
