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
# SocketPipeline.py
#
# This file holds the SocketPipeline class, which connects a Pipeline to a
# socket and manages connection/disconnection and everything.
#

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QSslSocket
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtNetwork import QAbstractSocket

from .Pipeline import Pipeline
from .AnsiFilter import AnsiFilter
from .TelnetFilter import TelnetFilter
from .TriggersFilter import TriggersFilter
from .FlowControlFilter import FlowControlFilter
from .UnicodeTextFilter import UnicodeTextFilter

from .ChunkData import ChunkType
from .ChunkData import NetworkState

from Messages import messages
from Utilities import check_ssl_is_available
from SingleShotTimer import SingleShotTimer


class SocketPipeline(QObject):
    def __init__(self, settings):

        super().__init__()

        self.net_settings = settings._net

        app = QApplication.instance()
        assert app is not None
        # TODO: Find a way to pass the core instance.
        self.triggersmanager = app.core.triggers  # type: ignore

        self.pipeline = Pipeline()

        self.pipeline.addFilter(TelnetFilter)
        self.pipeline.addFilter(AnsiFilter)
        self.pipeline.addFilter(
            UnicodeTextFilter, encoding=self.net_settings._encoding
        )
        self.pipeline.addFilter(FlowControlFilter)
        self.pipeline.addFilter(TriggersFilter, manager=self.triggersmanager)

        self.using_ssl = False
        self.socket = None
        self.buffer: list[bytes] = []

        self.flush_timer = SingleShotTimer(self.flushBuffer)

        self.net_settings.onChange("encoding", self.setStreamEncoding)

    def setStreamEncoding(self):

        if self.pipeline:
            self.pipeline.notify(
                "encoding_changed", self.net_settings._encoding
            )

    def setupSocket(self):

        if self.net_settings._ssl and check_ssl_is_available():

            self.using_ssl = True
            self.socket = QSslSocket()

            self.socket.encrypted.connect(self.reportEncrypted)  # type: ignore
            self.socket.sslErrors.connect(self.handleSslErrors)  # type: ignore

        else:
            self.socket = QTcpSocket()

            if (
                self.net_settings._ssl
            ):  # SSL was requested but is not available...
                messages.warn(
                    "SSL functions not available; attempting "
                    "unencrypted connection instead..."
                )

        self.socket.stateChanged.connect(self.reportStateChange)  # type: ignore
        self.socket.error.connect(self.reportError)  # type: ignore
        self.socket.readyRead.connect(self.readSocket)  # type: ignore

    def connectToHost(self):

        if not self.socket:
            self.setupSocket()
        assert self.socket is not None

        self.pipeline.resetInternalState()

        params = (self.net_settings._host, self.net_settings._port)

        if self.using_ssl:
            self.socket.connectToHostEncrypted(*params)  # type: ignore

        else:
            self.socket.connectToHost(*params)

    def disconnectFromHost(self):

        if self.socket:
            self.socket.disconnectFromHost()

    def abort(self):

        if self.socket:
            self.socket.abort()
            self.socket.close()

    @pyqtSlot("QAbstractSocket::SocketState")
    def reportStateChange(self, state):

        self.flushBuffer()

        if state == QAbstractSocket.SocketState.HostLookupState:
            self.pipeline.feedChunk((ChunkType.NETWORK, NetworkState.RESOLVING))

        elif state == QAbstractSocket.SocketState.ConnectingState:
            self.pipeline.feedChunk(
                (ChunkType.NETWORK, NetworkState.CONNECTING)
            )

        elif state == QAbstractSocket.SocketState.ConnectedState:
            self.pipeline.feedChunk((ChunkType.NETWORK, NetworkState.CONNECTED))

        elif state == QAbstractSocket.SocketState.UnconnectedState:
            self.pipeline.feedChunk(
                (ChunkType.NETWORK, NetworkState.DISCONNECTED)
            )

    @pyqtSlot()
    def reportEncrypted(self):

        self.flushBuffer()
        self.pipeline.feedChunk((ChunkType.NETWORK, NetworkState.ENCRYPTED))

    @pyqtSlot("QAbstractSocket::SocketError")
    def reportError(self, error):

        self.flushBuffer()

        if error == QAbstractSocket.SocketError.ConnectionRefusedError:
            self.pipeline.feedChunk(
                (ChunkType.NETWORK, NetworkState.CONNECTIONREFUSED)
            )

        elif error == QAbstractSocket.SocketError.HostNotFoundError:
            self.pipeline.feedChunk(
                (ChunkType.NETWORK, NetworkState.HOSTNOTFOUND)
            )

        elif error == QAbstractSocket.SocketError.SocketTimeoutError:
            self.pipeline.feedChunk((ChunkType.NETWORK, NetworkState.TIMEOUT))

        elif error == QAbstractSocket.SocketError.RemoteHostClosedError:
            pass  # It's okay, we handle it as a disconnect.

        else:
            self.pipeline.feedChunk(
                (ChunkType.NETWORK, NetworkState.OTHERERROR)
            )

    @pyqtSlot("const QList<QSslError> &")
    def handleSslErrors(self, errors):

        # We take note of the errors... and then discard them.
        # SSL validation errors are very common because many legitimate servers
        # are just not going to fork money over certificates, and nobody's
        # going to blame them for it.

        for err in errors:
            messages.warn("SSL Error: " + err.errorString())

        assert isinstance(self.socket, QSslSocket)
        self.socket.ignoreSslErrors()

    @pyqtSlot()
    def readSocket(self):

        if self.socket is None:
            return

        # PyQt auto-converts from C++ char* to Python bytes.
        data: bytes = self.socket.readAll().data()
        self.buffer.append(data)

        self.flush_timer.start()

    def flushBuffer(self):

        data = b"".join(self.buffer)
        del self.buffer[:]
        self.pipeline.feedBytes(data)

    def send(self, data: str):

        if self.socket is None:
            return

        if (
            not self.socket.state()
            == QAbstractSocket.SocketState.ConnectedState
        ):

            # Don't write anything if the socket is not connected.
            return

        encoding = self.net_settings._encoding
        databytes = self.pipeline.formatForSending(
            data.encode(encoding, errors="replace")
        )

        self.socket.write(databytes)
        self.socket.flush()

    def addSink(self, sink, types: int = ChunkType.all()) -> None:

        self.pipeline.addSink(sink, types)
