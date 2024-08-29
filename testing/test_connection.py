from pytest_mock import MockerFixture

from PySide6.QtNetwork import QTcpSocket

from spyrit.network.connection import Connection, ConnectionStatus, Status
from spyrit.settings.spyrit_settings import SpyritSettings


class TestConnection:
    def test_connection_reports_socket_state(
        self, mocker: MockerFixture
    ) -> None:
        connection = Connection(SpyritSettings.Network())

        slot = mocker.stub()
        connection.statusChanged.connect(slot)

        socket = connection._socket  # type: ignore

        socket.stateChanged.emit(QTcpSocket.SocketState.ConnectedState)
        slot.assert_called_once_with(Status.CONNECTED, "")
        slot.reset_mock()

        socket.stateChanged.emit(QTcpSocket.SocketState.ConnectingState)
        slot.assert_called_once_with(Status.CONNECTING, "")
        slot.reset_mock()

        socket.stateChanged.emit(QTcpSocket.SocketState.HostLookupState)
        slot.assert_called_once_with(Status.RESOLVING, "")
        slot.reset_mock()

        socket.stateChanged.emit(QTcpSocket.SocketState.UnconnectedState)
        slot.assert_called_once_with(Status.DISCONNECTED, "")
        slot.reset_mock()

        socket.setErrorString("Test!")
        socket.errorOccurred.emit(QTcpSocket.SocketError.ConnectionRefusedError)
        slot.assert_called_once_with(Status.ERROR, "Test!")
        slot.reset_mock()

    def test_connection_reports_socket_data(
        self, mocker: MockerFixture
    ) -> None:
        connection = Connection(SpyritSettings.Network())

        slot = mocker.stub()
        connection.dataReceived.connect(slot)

        socket = connection._socket  # type:ignore
        socket.isValid = mocker.Mock(return_value=True)
        socket.readAll = mocker.Mock(return_value=b"abcde")

        socket.readyRead.emit()
        slot.assert_called_once_with(b"abcde")


class TestConnectionStatus:
    def test_connection_status_is_accurate(self) -> None:
        connection = Connection(SpyritSettings.Network())

        status = ConnectionStatus(connection)

        assert not status.isConnecting()
        assert not status.isConnected()

        connection.statusChanged.emit(Status.RESOLVING, "")

        assert status.isConnecting()
        assert not status.isConnected()

        connection.statusChanged.emit(Status.CONNECTING, "")

        assert status.isConnecting()
        assert not status.isConnected()

        connection.statusChanged.emit(Status.CONNECTED, "")

        assert status.isConnecting()
        assert status.isConnected()

        connection.statusChanged.emit(Status.DISCONNECTED, "")

        assert not status.isConnecting()
        assert not status.isConnected()

        connection.statusChanged.emit(Status.CONNECTED, "")
        connection.statusChanged.emit(Status.ERROR, "")

        assert not status.isConnecting()
        assert not status.isConnected()

    def test_connection_status_changes_send_signals(
        self, mocker: MockerFixture
    ) -> None:
        connection = Connection(SpyritSettings.Network())

        status = ConnectionStatus(connection)

        connecting = mocker.Mock()
        connected = mocker.Mock()

        status.connecting.connect(connecting)
        status.connected.connect(connected)

        connection.statusChanged.emit(Status.DISCONNECTED, "")

        connecting.assert_not_called()
        connected.assert_not_called()

        connection.statusChanged.emit(Status.RESOLVING, "")

        connecting.assert_called_once_with(True)
        connecting.reset_mock()
        connected.assert_not_called()

        connection.statusChanged.emit(Status.CONNECTING, "")

        connecting.assert_not_called()
        connected.assert_not_called()

        connection.statusChanged.emit(Status.CONNECTED, "")

        connecting.assert_not_called()
        connected.assert_called_once_with(True)
        connected.reset_mock()

        connection.statusChanged.emit(Status.ERROR, "")

        connecting.assert_called_once_with(False)
        connecting.reset_mock()
        connected.assert_called_once_with(False)
        connected.reset_mock()

        connection.statusChanged.emit(Status.DISCONNECTED, "")

        connecting.assert_not_called()
        connected.assert_not_called()
