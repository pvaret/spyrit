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
Implements a class that handles the lifecycle of a network connection.
"""


import enum
import logging

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QTcpSocket

from spyrit.settings.spyrit_settings import SpyritSettings


class Status(enum.Enum):
    """
    The status of a network connection.
    """

    DISCONNECTED = enum.auto()
    RESOLVING = enum.auto()
    CONNECTING = enum.auto()
    CONNECTED = enum.auto()
    ERROR = enum.auto()


class Connection(QObject):
    """
    Implements the network connection to a game.

    Args:
        settings: The settings to use to configure this connection.

        parent: The object to use as this connection's parent. Used for lifetime
            management.
    """

    _settings: SpyritSettings.Network
    _socket: QTcpSocket
    _is_connected: bool

    # This signal is emitted when data is received from the socket.

    dataReceived: Signal = Signal(bytes)  # noqa: N815

    # This signal is emitted when the status of the connection changed.

    statusChanged: Signal = Signal(Status, str)  # noqa: N815

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
        """
        Initiates the process of connecting to the configured server.
        """

        if self._is_connected:
            return

        self._socket.abort()
        self._socket.connectToHost(
            self._settings.server.get(), self._settings.port.get()
        )

    def stop(self) -> None:
        """
        Disconnects from the configured server.
        """

        self._socket.disconnectFromHost()

    def send(self, data: str | bytes) -> bool:
        """
        Sends the given data to the server, if connected.

        Args:
            data: The piece of data to be sent. If data is a string, it is
                converted to bytes using the configured encoding.

        Returns:
            Whether the data was sent entirely.
        """

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

    def isConnected(self) -> bool:
        """
        Returns whether the connection is connected, i.e. the connection was
        successfully established and is currently live.

        Returns:
            Whether the connection is live.
        """

        return self._is_connected

    @Slot()
    def _readFromSocket(self) -> None:
        """
        Pulls data from the socket, if any, and processes it. I.e. emits the
        corresponding signal.
        """

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
        """
        Emits a status change signal to reflect the new status.

        Args:
            status: The new status that the socket is in.
        """

        match status:
            case QTcpSocket.SocketState.UnconnectedState:
                # Only report the disconnection if we were connected in the first
                # place.

                if self._is_connected:
                    self._is_connected = False
                    self.statusChanged.emit(Status.DISCONNECTED, "")

            case QTcpSocket.SocketState.HostLookupState:
                self.statusChanged.emit(
                    Status.RESOLVING, self._socket.peerName()
                )

            case QTcpSocket.SocketState.ConnectingState:
                self.statusChanged.emit(Status.CONNECTING, "")

            case QTcpSocket.SocketState.ConnectedState:
                self._is_connected = True
                self.statusChanged.emit(Status.CONNECTED, "")

            case (
                QTcpSocket.SocketState.BoundState
                | QTcpSocket.SocketState.ListeningState
                | QTcpSocket.SocketState.ClosingState
            ):
                pass

    @Slot()
    def _reportErrorOccurred(self) -> None:
        """
        Emits a signal to report the error that took place, if any.
        """

        error = self._socket.error()

        if error == QTcpSocket.SocketError.RemoteHostClosedError:
            # Server closed the connection. That's okay.

            return

        error_text = self._socket.errorString()
        self.statusChanged.emit(Status.ERROR, error_text)
