import errno
import fcntl

from pathlib import Path

from pytest import MonkeyPatch
from pytest_mock import MockFixture, MockerFixture

from PySide6.QtNetwork import QLocalServer, QLocalSocket

from spyrit.singletonizer import PIDFile, Singletonizer

_TEST_PID = 12345678


class TestPIDFile:
    def test_lock_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        pidfile = tmp_path / "subdir" / "test.pid"

        assert not pidfile.exists()

        stub_flock = mocker.Mock(spec=fcntl.flock)
        p = PIDFile(pidfile, _TEST_PID, _flock=stub_flock)

        assert p.tryLock()
        assert pidfile.exists()
        assert pidfile.read_text() == "12345678"

        stub_flock.assert_called_once()
        stub_flock.reset_mock()

        assert p.tryLock()
        assert pidfile.exists()
        assert pidfile.read_text() == "12345678"

        # fcntl.flock should not be called again if we already hold the lock.

        stub_flock.assert_not_called()

        p.unlock()
        assert not pidfile.exists()

    def test_lock_failed(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Make fcntl.flock raise an EAGAIN OSError.

        err = OSError()
        err.errno = errno.EAGAIN
        stub_flock = mocker.Mock(spec=fcntl.flock, side_effect=err)

        pidfile = tmp_path / "subdir" / "test.pid"

        assert not pidfile.exists()

        p = PIDFile(pidfile, _TEST_PID, _flock=stub_flock)

        assert not p.tryLock()
        assert not p.tryLock()

        p.unlock()


class TestSingletonizer:
    def test_singletonizer_main_instance(
        self, tmp_path: Path, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        stub_pidfile = mocker.Mock(spec=PIDFile)
        stub_server = mocker.Mock(spec=QLocalServer)
        stub_socket = mocker.Mock(spec=QLocalSocket)

        stub_pidfile.tryLock = mocker.Mock(return_value=True)
        stub_server.listen = mocker.Mock(return_value=True)

        stub_make_socket_name = mocker.Mock(return_value="test-socket-name")
        monkeypatch.setattr(
            Singletonizer, "_makeSocketName", stub_make_socket_name
        )

        singletonizer = Singletonizer(
            tmp_path / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )
        assert singletonizer.isMainInstance()
        assert singletonizer._server is not None  # type: ignore

        stub_server.listen.assert_called_once_with(  # type: ignore
            "test-socket-name"
        )

    def test_singletonizer_non_main_instance(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        stub_pidfile = mocker.Mock(spec=PIDFile)
        stub_server = mocker.Mock(spec=QLocalServer)
        stub_socket = mocker.Mock(spec=QLocalSocket)

        stub_pidfile.tryLock = mocker.Mock(return_value=False)

        singletonizer = Singletonizer(
            tmp_path / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )
        assert not singletonizer.isMainInstance()
        assert singletonizer._server is None  # type: ignore

        stub_server.listen.assert_not_called()  # type: ignore

    def test_socket_path(self, tmp_path: Path, mocker: MockerFixture) -> None:
        stub_pidfile = mocker.Mock(spec=PIDFile)
        stub_server = mocker.Mock(spec=QLocalServer)
        stub_socket = mocker.Mock(spec=QLocalSocket)

        stub_pidfile.tryLock = mocker.Mock(return_value=False)

        path_a = tmp_path / "pathA"
        path_b = tmp_path / "pathB"
        path_a.mkdir(parents=True)
        path_b.mkdir(parents=True)
        singletonizer_a1 = Singletonizer(
            path_a / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )
        singletonizer_a2 = Singletonizer(
            path_a / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )
        singletonizer_b = Singletonizer(
            path_b / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )

        assert (
            singletonizer_a1._makeSocketName()  # type: ignore
            == singletonizer_a2._makeSocketName()  # type: ignore
        )

        assert (
            singletonizer_a1._makeSocketName()  # type: ignore
            != singletonizer_b._makeSocketName()  # type: ignore
        )

    def test_shutdown(self, tmp_path: Path, mocker: MockFixture) -> None:
        stub_pidfile = mocker.Mock(spec=PIDFile)
        stub_server = mocker.Mock(spec=QLocalServer)
        stub_socket = mocker.Mock(spec=QLocalSocket)

        stub_pidfile.tryLock = mocker.Mock(return_value=True)
        stub_server.listen = mocker.Mock(return_value=True)

        singletonizer = Singletonizer(
            tmp_path / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )

        assert singletonizer.isMainInstance()
        assert singletonizer._server is not None  # type: ignore
        singletonizer.shutdown()
        assert singletonizer._server is None  # type: ignore
        assert not singletonizer.isMainInstance()

    def test_secondary_instance_notification_received(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        stub_pidfile = mocker.Mock(spec=PIDFile)
        stub_socket = mocker.Mock(spec=QLocalSocket)
        stub_server = mocker.Mock(spec=QLocalServer)

        stub_pidfile.tryLock = mocker.Mock(return_value=True)
        stub_server.listen = mocker.Mock(return_value=True)
        stub_server.hasPendingConnections = mocker.Mock(
            side_effect=[True, False]
        )
        stub_server.nextPendingConnection = mocker.Mock(
            return_value=stub_socket
        )

        singletonizer = Singletonizer(
            tmp_path / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )

        stub_slot = mocker.stub()
        singletonizer.newInstanceStarted.connect(stub_slot)

        singletonizer._onNewConnectionReceived()  # type: ignore

        stub_socket.readAll.assert_called_once()  # type: ignore
        stub_slot.assert_called_once()

    def test_send_secondary_instance_notification(
        self, tmp_path: Path, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        stub_pidfile = mocker.Mock(spec=PIDFile)
        stub_server = mocker.Mock(spec=QLocalServer)
        stub_socket = mocker.Mock(spec=QLocalSocket)

        stub_pidfile.tryLock = mocker.Mock(return_value=False)

        stub_make_socket_name = mocker.Mock(return_value="test-socket-name")
        monkeypatch.setattr(
            Singletonizer, "_makeSocketName", stub_make_socket_name
        )

        singletonizer = Singletonizer(
            tmp_path / "test.pid",
            _pidfile_factory=lambda _: stub_pidfile,
            _server_factory=lambda _: stub_server,
            _socket_factory=lambda: stub_socket,
        )
        singletonizer.notifyNewInstanceStarted()

        stub_socket.connectToServer.assert_called_once_with(  # type: ignore
            "test-socket-name"
        )
        stub_socket.write.assert_called_once()  # type: ignore
