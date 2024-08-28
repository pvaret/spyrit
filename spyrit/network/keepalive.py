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
Implements a class that periodically sends a message on an active connection so
that the connection is not considered idle and reset by the server, or, say,
CGNATs.
"""


import logging

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from spyrit.network.connection import Connection, Status
from spyrit.settings.spyrit_settings import SpyritSettings


class Keepalive(QObject):
    # This signal fires when this object wishes to send a keepaline ping.

    keepalive: Signal = Signal(bytes)

    _settings: SpyritSettings.Network.Keepalive
    _timer: QTimer
    _connected: bool = False

    def __init__(
        self,
        connection: Connection,
        settings: SpyritSettings.Network.Keepalive,
        timer: QTimer | None = None,
    ) -> None:
        super().__init__(connection)

        self._timer = timer if timer is not None else QTimer()
        self._timer.timeout.connect(self._sendKeepalive)

        self._settings = settings
        self._settings.enabled.onValueChangeCall(self._maybeStartTimer)
        self._settings.period_secs.onValueChangeCall(self._setTimerTimeout)
        self._setTimerTimeout(settings.period_secs.get())

        connection.statusChanged.connect(self._connectionStatusChanged)
        self.keepalive.connect(connection.send)

    def _setTimerTimeout(self, secs: int) -> None:
        self._timer.setInterval(secs * 1000)

    def _sendKeepalive(self) -> None:
        logging.debug("Sending keep-alive message.")
        self.keepalive.emit(self._settings.message.get().value)

    @Slot(Status)
    def _connectionStatusChanged(self, status: Status) -> None:
        self._connected = status == Status.CONNECTED
        self._maybeStartTimer(self._settings.enabled.get())

    def _maybeStartTimer(self, enabled: bool) -> None:
        if enabled and self._connected:
            self._timer.start()
        else:
            self._timer.stop()
