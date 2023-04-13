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
Holds a class that helps ensure only one instance of the application is running.
"""

import errno
import fcntl
import logging
import os
import threading

from pathlib import Path
from types import TracebackType
from typing import IO, Callable, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from spyrit import constants


class PIDFile:
    """
    Maintains a locked PID file that can only be owned by one process at a time.

    Args:
        path: The full path to the PID file. The file and its parent directories
            will be created if they don't yet exist.

        pid: The PID to be written in the PID file. Default: the PID of the
            running process.
    """

    _path: Path
    _pid: int
    _fd: Optional[IO[str]]
    _lock: threading.Lock
    _flock_func: Callable[[IO[str], int], None]

    def __init__(
        self,
        path: Path,
        pid: int = os.getpid(),
        _flock: Callable[[IO[str], int], None] = fcntl.flock,
    ) -> None:
        self._lock = threading.Lock()
        self._path = path.resolve().absolute()
        self._pid = pid
        self._fd = None
        self._flock_func = _flock

    def tryLock(self) -> bool:
        """
        Attempt to secure sole ownership of the PID file. Write the PID to the
        file if successful.

        Can safely be called multiple times.

        May raise OSError if the PID file path is not writable.

        Returns:
            Whether the current process is the owner of the PID file.
        """

        with self._lock:
            self._ensureFileExists()

            if self._fd is not None:
                # Lock is in fact already held.

                return True

            try:
                fd = self._path.open()

            except OSError as e:
                logging.error(f"Error while opening PID file {self._path}: {e}")
                raise

            try:
                # Lock the file exclusively, in a non-blocking operation.

                self._flock_func(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                logging.debug(f"PID file {self._path} successfully locked.")

            except OSError as e:
                if e.errno != errno.EAGAIN:
                    logging.error(f"Failed to lock PID file {self._path}: {e}")
                    raise

                # EAGAIN means someone else owns the lock. That's fine.

                return False

            # Note that we only store the file descriptor if the locking
            # succeeded.

            self._fd = fd

            try:
                self._path.open("w").write(f"{self._pid}")
            except OSError as e:
                # Failed to write the PID in the file. That's actually not a
                # huge deal. The locking is the important part, and at this
                # point, it succeeded.

                logging.debug(f"Failed to write PID file {self._path}: {e}")

            return True

    def unlock(self) -> None:
        """
        Relinquish ownership of the PID file.

        Can safely be called even if this process is not the current owner of
        the PID file.
        """

        with self._lock:
            if self._fd is not None:
                try:
                    self._flock_func(self._fd, fcntl.LOCK_UN)

                except OSError:
                    # Not a big deal if this fails, we're going to delete the
                    # file anyway.

                    pass

                self._path.unlink()
                self._fd.close()
                self._fd = None

    def _ensureFileExists(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.touch()

        except OSError as e:
            logging.error(f"Error while creating PID file {self._path}: {e}")
            raise


class Singletonizer(QObject):
    """
    Helper class that can detect if this process is the main instance of the
    program, and provides IPC to let new instances notify the main instance of
    their existence.

    It can be used as a context manager, in which case it will automatically
    clean up its resources when exiting.

    Args:
        pidfile: The path to the file where to store the process PID.
    """

    # Signal that is emitted when another process instance of this program
    # notified this one that it started.

    newInstanceStarted = Signal()  # noqa: N815

    _path: Path
    _pidfile: Optional[PIDFile]
    _server: Optional[QLocalServer]
    _socket_name: str
    _socket_factory: Callable[[], QLocalSocket]

    def __init__(
        self,
        pidfile: Path,
        _pidfile_factory: Callable[[Path], PIDFile] = PIDFile,
        _server_factory: Callable[[QObject], QLocalServer] = QLocalServer,
        _socket_factory: Callable[[], QLocalSocket] = QLocalSocket,
    ) -> None:
        super().__init__()

        self._server = None
        self._path = pidfile
        self._pidfile = _pidfile_factory(self._path)
        self._socket_name = ""
        self._socket_factory = _socket_factory

        if self._pidfile.tryLock():
            logging.info(
                f"Main process instance running with PID {os.getpid()}."
            )
            server = _server_factory(self)
            server.setSocketOptions(
                QLocalServer.SocketOption.AbstractNamespaceOption
            )
            self._socket_name = self._makeSocketName()

            # Remove an existing socket, if any. This can happen if an instance
            # previously crashed.

            server.removeServer(self._socket_name)

            logging.debug(
                "Starting singleton server on named socket"
                f" '{self._socket_name}'..."
            )

            if not server.listen(self._socket_name):
                logging.error(
                    f"Failed to create named socket '{self._socket_name}' for"
                    f" singleton server: {server.errorString()}"
                )
                return

            # Note that self._server is only set if this instance is the main
            # one.

            self._server = server
            self._server.newConnection.connect(self._onNewConnectionReceived)

        else:
            logging.debug(
                f"Process with PID {os.getpid()} is not the main instance."
            )

    def __enter__(self) -> "Singletonizer":
        return self

    def __exit__(
        self,
        __exc_type: Optional[type[BaseException]],
        __exc_value: Optional[BaseException],
        __traceback: Optional[TracebackType],
    ) -> None:
        self.shutdown()

    def isMainInstance(self) -> bool:
        """
        Returns whether this process is the main instance of this program
        running.
        """

        return self._pidfile is not None and self._pidfile.tryLock()

    def notifyNewInstanceStarted(self) -> None:
        """
        Lets the main instance of this program, if any, know that a new instance
        is trying to start.
        """

        socket_name = self._makeSocketName()
        conn = self._socket_factory()

        logging.debug(
            "Attempting connection to singleton server on named socket"
            f" '{socket_name}'..."
        )

        conn.setSocketOptions(QLocalSocket.SocketOption.AbstractNamespaceOption)
        conn.connectToServer(socket_name)
        if not conn.waitForConnected(msecs=1000):
            logging.error(
                "Failed to connect to singleton server on named socket"
                f" '{socket_name}: {conn.errorString()}'"
            )
            return

        conn.write(b"\0")
        conn.waitForBytesWritten(msecs=1000)
        conn.close()
        conn.deleteLater()

    def shutdown(self) -> None:
        """
        Release the singleton lock and clean up resources.

        This method is safe to call regardless of whether this instance is the
        main one.
        """

        if self._server is not None:
            self._server.close()
            self._server.removeServer(self._socket_name)
            self._server.deleteLater()
            self._server = None

        if self._pidfile is not None:
            if self._pidfile.tryLock():
                self._pidfile.unlock()
            self._pidfile = None

    def _onNewConnectionReceived(self) -> None:
        if self._server is None:
            return

        while self._server.hasPendingConnections():
            conn = self._server.nextPendingConnection()
            conn.readAll()
            conn.close()
            conn.deleteLater()
            self.newInstanceStarted.emit()

    def _makeSocketName(self) -> str:
        """
        Returns a local server socket name that's unique to the directory of the
        pidfile.
        """

        socket_name = f"singleton~{constants.APPLICATION_NAME}"

        dir = self._path.parent
        try:
            stat = dir.stat()
            socket_name = f"{socket_name}~{stat.st_dev}~{stat.st_ino}"
        except OSError:
            pass

        return socket_name
