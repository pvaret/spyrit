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
# ActionSet.py
#
# This holds the ActionSet class, which abstracts the QActions used by the
# software.
#


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication


class ActionSet:
    def __init__(self, parent):

        self.parent = parent

        settings = QApplication.instance().core.settings
        self.closures = []

        self.actions = {
            # Global actions
            "about": ("About %s..." % settings._app._name, ":/app/icon"),
            "aboutqt": ("About Qt...", ":/icon/qt-logo"),
            "newworld": ("New world...", ":/icon/new_world"),
            "quickconnect": ("Quick connect...", None),
            "quit": ("Quit", ":/icon/quit"),
            "nexttab": ("Next Tab", None),
            "previoustab": ("Previous Tab", None),
            "closetab": ("Close Tab", ":/icon/close"),
            # Per-world actions
            "connect": ("Connect", ":/icon/connect"),
            "disconnect": ("Disconnect", ":/icon/disconnect"),
            "historyup": ("History up", ":/icon/up"),
            "historydown": ("History down", ":/icon/down"),
            "autocomplete": ("Autocomplete", None),
            "pageup": ("Page up", ":/icon/up"),
            "pagedown": ("Page down", ":/icon/down"),
            "stepup": ("Step up", None),
            "stepdown": ("Step down", None),
            "home": ("Home", None),
            "end": ("End", None),
            "startlog": ("Start log", ":/icon/log_start"),
            "stoplog": ("Stop log", ":/icon/log_stop"),
            "toggle2ndinput": ("Toggle secondary input", None),
        }

        # Very few actions have a specific role, so it's more effective to put
        # roles in their own structure rather than in the one above.

        self.roles = {
            "about": QAction.AboutRole,
            "aboutqt": QAction.AboutQtRole,
            "quit": QAction.QuitRole,
        }

        # Likewise, custom shortcut contexts.

        self.contexts = {
            "historyup": Qt.WidgetShortcut,
            "historydown": Qt.WidgetShortcut,
            "autocomplete": Qt.WidgetShortcut,
        }

    def bindAction(self, action, slot):

        text, icon = self.actions[action]

        a = QAction(text, self.parent)

        if icon:
            a.setIcon(QIcon(icon))

        settings = QApplication.instance().core.settings._shortcuts

        def set_action_shortcut():

            # Note how this closure uses 'settings', 'a' and 'action' as bound
            # variables.

            shortcut = settings[action]

            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            else:
                a.setShortcut(QKeySequence())

        # Call it once:
        set_action_shortcut()

        settings.onChange(action, set_action_shortcut)

        # Keep a reference to the closure, so it's not garbage-collected
        # right away.
        self.closures.append(set_action_shortcut)

        role = self.roles.get(action)

        if role is not None:
            a.setMenuRole(role)

        context = self.contexts.get(action)

        if context is not None:
            a.setShortcutContext(context)

        a.triggered.connect(slot)

        # It is necessary to add the action to a widget before its shortcuts will
        # work.
        self.parent.addAction(a)

        return a
