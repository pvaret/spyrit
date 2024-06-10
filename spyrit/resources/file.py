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

import zlib

from io import DEFAULT_BUFFER_SIZE, BufferedIOBase, BufferedReader, RawIOBase
from typing import Any, MutableSequence
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


class ZlibIOWrapper(BufferedIOBase):
    """
    Wraps an IO object containing zlib-compressed data and exposes the
    decompressed data as a buffered IO object.

    Args:
        buffer: An IO object containing zlib or gzip compressed data.

        wbits: The window size, as defined in
            https://docs.python.org/3/library/zlib.html. The default value is
            configured for gzip-compressed data.
    """

    _input: BufferedIOBase
    _buffer: bytearray
    _decompressor: Any  # Sadly zlib does not expose its internal types.

    def __init__(
        self,
        buffer: BufferedIOBase | RawIOBase,
        wbits: int = zlib.MAX_WBITS | 16,
    ) -> None:
        super().__init__()

        if isinstance(buffer, RawIOBase):
            buffer = BufferedReader(buffer)

        self._input = buffer
        self._buffer = bytearray()
        self._decompressor = zlib.decompressobj(wbits)

    def read(self, size: int | None = -1) -> bytes:
        """
        Decompresses and returns the requested number of bytes from the
        underlying IO object.

        Args:
            size: How many bytes to decompress and return. If None or a negative
                value, decompress and return the entire stream.

        Returns:
            The decompressed bytes. If the end of the compressed stream is
            reached in the underlying IO object, returns an empty bytes object.
        """

        if self.closed:
            raise ValueError("File object is closed and cannot be read from.")

        if size is None:
            size = -1
        forever = size < 0

        while forever or len(self._buffer) < size:
            block = self._input.read(DEFAULT_BUFFER_SIZE)
            if not block:
                break
            block = self._decompressor.decompress(block)
            self._buffer.extend(block)

        if forever:
            ret = self._buffer
            self._buffer = bytearray()
        else:
            ret, self._buffer = self._buffer[:size], self._buffer[size:]

        return bytes(ret)

    def close(self) -> None:
        self._input.close()

    @property
    def closed(self) -> bool:
        return self._input.closed

    def readable(self) -> bool:
        return True
