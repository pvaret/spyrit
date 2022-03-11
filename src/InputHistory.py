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
# InputHistory.py
#
# Holds the InputHistory class, which manages the history of what the user
# typed in the input widget.
#


from PyQt5.QtGui import QTextCursor


class InputHistory:
    def __init__(self, inputwidget, shouldsave=True):

        self.inputwidget = inputwidget
        self.cursor = -1
        self.currenttext = ""
        self.shouldsave = shouldsave

        settings = inputwidget.world.settings
        state = inputwidget.world.state

        if self.shouldsave and settings._ui._input._save_history:

            try:
                count = int(settings._ui._input._save_history)

            except ValueError:
                count = 0

            self.history = state._ui._input._history[:count]

        else:
            self.history = []

    def historyUp(self):

        if len(self.history) == 0 or self.cursor >= len(self.history) - 1:
            return

        self.cursor += 1

        if self.cursor == 0:
            self.currenttext = self.inputwidget.toPlainText()

        self.inputwidget.setPlainText(self.history[self.cursor])
        self.inputwidget.moveCursor(QTextCursor.End)

    def historyDown(self):

        if self.cursor < 0:
            return

        self.cursor -= 1

        if self.cursor == -1:
            self.inputwidget.setPlainText(self.currenttext)

        else:
            self.inputwidget.setPlainText(self.history[self.cursor])

        self.inputwidget.moveCursor(QTextCursor.End)

    def update(self, text):

        self.currenttext = ""
        self.cursor = -1

        # Don't update if text hasn't changed:

        if self.history and self.history[0] == text:
            return

        self.history.insert(0, text)

        settings = self.inputwidget.world.settings
        state = self.inputwidget.world.state

        maxlength = settings._ui._input._max_history

        if maxlength and len(self.history) > maxlength:
            self.history.pop()

        count = int(settings._ui._input._save_history)
        if self.shouldsave and count:
            state._ui._input._history = self.history[:count]
