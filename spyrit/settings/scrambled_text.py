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
Provides a class that can be used to save text in settings in a scrambled form.
"""

import base64
import binascii
import hashlib
import random

from typing import Iterator


def _pads(salt: bytes) -> Iterator[bytes]:
    """
    Uses the provided input to generate an infinite series of deterministic
    pads.

    The pads can be used for scrambling purposes, but should not be used for
    anything cryptographically sensitive.

    Args:
        salt: The input from which to derive the pads.

    Returns:
        A series of pads. XOR them to an input in order to scramble it.
    """

    SEEKRIT = base64.b64decode(
        b"cG8tVEFZLXRvIHBvLVRBSC10bzqZDaAFScI0+"
        b"jL2uLHxQy3wHK+grcOxEcWJUZLQq6kO4w=="
    )

    hash = hashlib.sha256(salt)
    hash.update(SEEKRIT)
    pad = hash.digest()

    while True:
        yield pad
        pad = hashlib.sha256(pad).digest()


class ScrambledText:
    """
    An implementation of the sunset.Serializable protocol that stores text
    scrambled.

    !! The scrambling is not cryptographically secure. !!

    Don't use it for anything sensitive.

    Args:
        plaintext: The text to store scrambled. It should not contain the NULL
            character (U+0000).

        salt: The salt with which to scramble the text. If None, a random salt
            will be generated. It's an error to pass a salt of a length other
            than ScrambleText.SALT_LENGTH.
    """

    SALT_LENGTH: int = 16
    TEXT_ENCODING = "utf8"  # can encode any character
    B64_ENCODING = "latin1"  # can decode any bytestring

    _salt: bytes
    _cipher: bytes

    def __init__(self, plaintext: str, salt: bytes | None = None) -> None:
        self._salt = salt or random.randbytes(self.SALT_LENGTH)
        assert len(self._salt) == self.SALT_LENGTH

        self._cipher = self._scramble(
            self._salt, plaintext.encode(self.TEXT_ENCODING)
        )

    def plaintext(self) -> str:
        """
        Descrambles and returns the plain text string that was used to create
        this ScrambledText instance.

        Returns:
            The original plain text string.
        """

        return (
            self._scramble(self._salt, self._cipher)
            .rstrip(b"\0")
            .decode(self.TEXT_ENCODING, errors="ignore")
        )

    def toStr(self) -> str:
        """
        Constructs and returns a scrambled string that is not legible on its
        own, but can be used by fromStr() to reconstruct the original
        ScrambledText instance.

        Returns:
            An opaque string usable only by fromStr().
        """

        payload = self._salt + self._cipher

        return base64.b64encode(payload).decode(self.B64_ENCODING)

    @classmethod
    def fromStr(cls, text: str) -> "ScrambledText | None":
        """
        Turns a scrambled string back into a ScrambledText instance.

        Args:
            text: The output of a ScrambledText.toStr() call.

        Returns:
            A ScrambleText instance identical to the one used to create the
            scrambled string. None if the input is invalid.
        """

        try:
            payload = base64.b64decode(
                text.encode(cls.B64_ENCODING), validate=True
            )
        except (UnicodeEncodeError, ValueError, binascii.Error):
            return None

        salt, cipher = payload[: cls.SALT_LENGTH], payload[cls.SALT_LENGTH :]
        if len(salt) != cls.SALT_LENGTH:
            return None

        cipher = cls._scramble(salt, cipher)

        try:
            plaintext = cipher.rstrip(b"\0").decode(cls.TEXT_ENCODING)
        except UnicodeDecodeError:
            return None

        return cls(plaintext, salt)

    @staticmethod
    def _scramble(salt: bytes, payload: bytes) -> bytes:
        """
        Scrambles the given payload, using the given salt to generate the XOR
        pad.

        Args:
            salt: A random bytestring.

            payload: The bytestring to scramble or descramble.

        Returns:
            The payload, scrambled or descrambled.
        """

        scrambled = b""

        for pad in _pads(salt):
            if not payload:
                break

            payload, block = payload[len(pad) :], payload[: len(pad)]

            if len(block) < len(pad):
                block += b"\0" * (len(pad) - len(block))

            assert len(block) == len(pad)
            scrambled += bytes(b ^ p for b, p in zip(block, pad))

        return scrambled
