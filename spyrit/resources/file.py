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
Implements a Pythonic file wrapper around Qt resources.
"""

from io import RawIOBase
from typing import MutableSequence
from typing_extensions import Buffer

from PySide6.QtCore import QFile

from spyrit.resources.resources import _Resource  # type: ignore


class ResourceFile(RawIOBase):
    """
    Implements a read-only RawIOBase wrapper around a Qt resource.

    Args:
        resource: The id of resource to be wrapped into a RawIOBase. The
            resource needs to be already loaded.
    """

    _file: QFile

    def __init__(self, resource: _Resource) -> None:
        super().__init__()
        self._file = QFile(resource)
        self._file.open(QFile.OpenModeFlag.ReadOnly)

    def readinto(self, buffer: Buffer) -> int:
        """
        Practical implementation of RawIOBase.readinto().

        Args:
            buffer: A buffer type that implements the MutableSequence protocol.
                Its length will be used to determine the size of the read
                operation. If the buffer does not implement the MutableSequence
                protocol, a type error will be raised.

        Returns:
            The number of bytes read. Will be 0 when reaching the end of the
            resource data.
        """

        if not isinstance(buffer, MutableSequence):
            raise TypeError(
                f"Input parameter must be a mutable sequence; got {type(buffer)}."
            )

        if self.closed:
            raise ValueError("File object is closed and cannot be read from.")

        size = len(buffer)
        data = self._file.read(size)
        buffer[:] = data.data()
        return len(buffer)

    def readall(self) -> bytes:
        """
        Practical implementation of RawIOBase.readall().

        Returns:
            The remainder of the contents of the file.
        """

        if self.closed:
            raise ValueError("File object is closed and cannot be read from")

        return bytes(self._file.readAll().data())

    def close(self) -> None:
        self._file.close()

    @property
    def closed(self) -> bool:
        return not self._file.isOpen()

    def readable(self) -> bool:
        return True
