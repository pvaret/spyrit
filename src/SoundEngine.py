# -*- coding: utf-8 -*-

# Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
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
# SoundEngine.py
#
# Contains the SoundEngine class, our simple sound player. It tries to locate
# a backend that works on the user's platform and then uses it for playback.
#


import os.path

from QSoundBackend import QSoundBackend
from PygameBackend import PygameBackend
from PlatformSpecific import platformSpecific


class SoundBackendRegistry:

    SOUNDBACKENDS = {
        "qsound": QSoundBackend,
        "pygame": PygameBackend,
    }

    def __init__(self):

        self.preferred_backends = platformSpecific.get_sound_backends()
        self.backend_cache = {}

    def pollForBackend(self):

        for backend_name in self.preferred_backends:

            backend = self.lookupBackend(backend_name)

            if backend.isAvailable():
                return backend

        return None

    def lookupBackend(self, backend_name):

        if backend_name not in self.backend_cache:
            self.backend_cache[backend_name] = self.SOUNDBACKENDS[
                backend_name
            ]()

        return self.backend_cache[backend_name]

    def listBackends(self, also_list_unsupported=False):

        if also_list_unsupported:
            backend_list = self.SOUNDBACKENDS.keys()
        else:
            backend_list = self.preferred_backends

        return [
            self.lookupBackend(backend_name) for backend_name in backend_list
        ]


class SoundEngine:
    def __init__(self, tmprc):

        self.tmprc = tmprc
        self.registry = SoundBackendRegistry()
        self.backend = self.registry.pollForBackend()

    def play(self, soundfile):

        if not self.backend:
            return False, "No sound engine available."

        filename = self.tmprc.get(soundfile)

        if not os.path.exists(filename):
            return False, "%s: file not found." % soundfile

        if not os.path.isfile(filename):
            return False, "%s: not a valid file." % soundfile

        # TODO: Check that filename is a valid WAV file.

        self.backend.play(filename)
        return True, None
