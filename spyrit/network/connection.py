# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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

"""
Implements class that handles the lifecycle of a network connection.
"""


from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QTcpSocket

from spyrit.settings.spyrit_settings import SpyritSettings


class Connection(QObject):
    """
    Implements the network connection to a game.
    """

    _settings: SpyritSettings.Network
    _socket: QTcpSocket

    # This signal is emited when data is received from the socket.

    dataReceived = Signal(bytes)  # noqa: N815

    def __init__(
        self, settings: SpyritSettings.Network, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)

        self._settings = settings
        self._socket = QTcpSocket(self)
        self._socket.readyRead.connect(self._readFromSocket)

    def start(self) -> None:
        if self._socket.state() == QTcpSocket.SocketState.ConnectedState:
            return

        self._socket.abort()
        self._socket.connectToHost(
            self._settings.server.get(), self._settings.port.get()
        )

    def stop(self) -> None:
        self._socket.disconnectFromHost()

    def send(self, data: str | bytes) -> bool:
        if isinstance(data, str):
            data = data.encode(self._settings.encoding.get().value, "ignore")

        if not self._socket.isValid():
            return False

        while data:
            i = self._socket.write(data)
            if i <= 0:
                return False

            data = data[i:]

        return True

    def _readFromSocket(self) -> None:
        if not self._socket.isValid():
            return

        data = self._socket.readAll()
        if not data:
            return

        byte_data = bytes(data)  # type: ignore  # Actually valid!
        self.dataReceived.emit(byte_data)
