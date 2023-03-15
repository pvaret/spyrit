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
# PygameBackend.py
#
# Implements the pygame-based sound backend.
# This is mostly used on Linux, where it might be the most readily
# available backend.
#


_pygame_is_available = False

try:
    import pygame  # type: ignore  # it's okay if this is missing.

    _pygame_is_available = True

except ImportError:
    # Pygame not found. Bummer.
    pass


FREQUENCY = 44100  # hz
SIZE = -16  # 16 bits, signed
CHANNELS = 1  # mono
BUFFER = 1024  # bytes


class PygameBackend:
    name = "SDL"

    def __init__(self):
        self.mixer = None

    def isAvailable(self) -> bool:
        if not _pygame_is_available:
            return False

        self.mixer = pygame.mixer

        try:
            self.mixer.init(FREQUENCY, SIZE, CHANNELS, BUFFER)

        except pygame.error:
            return False

        return True

    def play(self, soundfile: str) -> None:
        if self.mixer:
            sound = self.mixer.Sound(soundfile)
            sound.play()

    def __del__(self) -> None:
        if self.mixer:
            self.mixer.quit()
