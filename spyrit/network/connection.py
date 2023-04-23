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
Implements a class that handles the lifecycle of a network connection.
"""


import enum
import logging

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QTcpSocket

from spyrit.settings.spyrit_settings import SpyritSettings


class Status(enum.Enum):
    DISCONNECTED = enum.auto()
    RESOLVING = enum.auto()
    CONNECTING = enum.auto()
    CONNECTED = enum.auto()
    ERROR = enum.auto()


class Connection(QObject):
    """
    Implements the network connection to a game.
    """

    _settings: SpyritSettings.Network
    _socket: QTcpSocket
    _is_connected: bool

    # This signal is emited when data is received from the socket.

    dataReceived = Signal(bytes)  # noqa: N815

    # This signal is emited when the status of the connection changed.

    statusChanged = Signal(Status, str)  # noqa: N815

    def __init__(
        self, settings: SpyritSettings.Network, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)

        self._is_connected = False
        self._settings = settings
        self._socket = QTcpSocket(self)
        self._socket.readyRead.connect(self._readFromSocket)
        self._socket.stateChanged.connect(self._reportStatusChange)
        self._socket.errorOccurred.connect(self._reportErrorOccurred)

    def start(self) -> None:
        if self._is_connected:
            return

        self._socket.abort()
        self._socket.connectToHost(
            self._settings.server.get(), self._settings.port.get()
        )

    def stop(self) -> None:
        self._socket.disconnectFromHost()

    def send(self, data: str | bytes) -> bool:
        if isinstance(data, str):
            data = data.encode(self._settings.encoding.get(), "ignore")

        if not self._socket.isValid():
            return False

        while data:
            i = self._socket.write(data)
            if i <= 0:
                return False

            data = data[i:]

        return True

    @Slot()
    def _readFromSocket(self) -> None:
        if not self._socket.isValid():
            return

        data = self._socket.readAll()
        if not data:
            return

        byte_data = bytes(data)  # type: ignore  # Actually valid!
        logging.debug(
            "Received data packet of length %d bytes.", len(byte_data)
        )
        self.dataReceived.emit(byte_data)

    @Slot(QTcpSocket.SocketState)
    def _reportStatusChange(self, status: QTcpSocket.SocketState) -> None:
        if status == QTcpSocket.SocketState.UnconnectedState:
            # Only report the disconnection if we were connected in the first
            # place.

            if self._is_connected:
                self._is_connected = False
                self.statusChanged.emit(Status.DISCONNECTED, "")

        elif status == QTcpSocket.SocketState.HostLookupState:
            self.statusChanged.emit(Status.RESOLVING, self._socket.peerName())

        elif status == QTcpSocket.SocketState.ConnectingState:
            self.statusChanged.emit(Status.CONNECTING, "")

        elif status == QTcpSocket.SocketState.ConnectedState:
            self._is_connected = True
            self.statusChanged.emit(Status.CONNECTED, "")

    @Slot()
    def _reportErrorOccurred(self) -> None:
        error = self._socket.error()

        if error == QTcpSocket.SocketError.RemoteHostClosedError:
            # Server closed the connection. That's okay.

            return

        error_text = self._socket.errorString()
        self.statusChanged.emit(Status.ERROR, error_text)
