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
Provides helpers that keep track of the visibility and focus of a given widget,
and send signals when the user's attention is needed.
"""

from PySide6.QtCore import QEvent, QObject, Signal, Slot
from PySide6.QtGui import QHideEvent, QShowEvent
from PySide6.QtWidgets import QWidget


class ActivityMonitor(QObject):
    """
    Monitors the visibility and window focus of the given widget. Emits a signal
    when the widget becomes active or inactive.
    """

    # This signal fires when the target widget becomes active or inactive, where
    # active means that it's both visible, and in a window that currently has
    # the focus.

    activityChanged: Signal = Signal(bool)

    _visible: bool
    _focused: bool
    _enabled: bool
    _active: bool

    def __init__(self, widget: QWidget) -> None:
        super().__init__(widget)

        self._visible = widget.isVisible()
        self._focused = widget.isActiveWindow()
        self._enabled = widget.isEnabled()
        self._active = self._focused and self._visible and self._enabled

        widget.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.parent() and isinstance(watched, QWidget):
            match event:
                case QShowEvent():
                    self._setVisible(True)
                case QHideEvent():
                    self._setVisible(False)
                case _ if event.type() == QEvent.Type.WindowActivate:
                    self._setFocused(True)
                case _ if event.type() == QEvent.Type.WindowDeactivate:
                    self._setFocused(False)
                case _ if event.type() == QEvent.Type.EnabledChange:
                    self._setEnabled(watched.isEnabled())
                case _:
                    pass
        return super().eventFilter(watched, event)

    def _setVisible(self, visible: bool) -> None:
        self._visible = visible
        self._updateActivity()

    def _setFocused(self, focused: bool) -> None:
        self._focused = focused
        self._updateActivity()

    def _setEnabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._updateActivity()

    def _updateActivity(self) -> None:
        active = self._focused and self._visible and self._enabled
        if active != self._active:
            self._active = active
            self.activityChanged.emit(active)

    def active(self) -> bool:
        return self._active


class AttentionPinger(QObject):
    # This signal fires when the user's attention is needed about a widget that
    # is not currently active.

    callForAttention: Signal = Signal()

    # This signal fires when the user gave their attention to the widget and the
    # attention call is no longer needed.

    clearAttentionCall: Signal = Signal()

    _active: bool = False

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)

    @Slot(bool)
    def setActive(self, active: bool) -> None:
        if active != self._active:
            self._active = active
            if active:
                self.clearAttentionCall.emit()

    @Slot()
    def maybeCallForAttention(self) -> None:
        if not self._active:
            self.callForAttention.emit()
