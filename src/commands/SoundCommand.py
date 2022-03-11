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
# SoundCommand.py
#
# Play sounds and manage sound engines.
#


import os.path

from PyQt5.QtWidgets import QApplication

from .BaseCommand import BaseCommand
from Utilities import format_as_table


class SoundCommand(BaseCommand):

    """Sound-related operations."""

    def cmd_play(self, world, filename=":/sound/pop"):

        """
        Play a sound.

        Usage: %(cmd)s [<soundfile.wav>]

        If you omit the sound file name, a default 'pop' sound will be played.
        The purpose of this command is to test your sound setup.

        """

        sound = QApplication.instance().core.sound

        filename = os.path.expanduser(filename)
        ok, msg = sound.play(filename)

        if not ok:
            world.info(msg)

    def cmd_engines(self, world, all=None):

        """
        List supported sound engines and their status.

        Usage: %(cmd)s [all]

        If the optional parameter 'all' is given, then all the existing engines
        will be listed, even if unsupported on your platform. Mind that polling
        unsupported engines may take a few seconds.

        Sound engines are listed with their status: available, not available,
        or in use. If no engine is in use, no sound can be played.

        """

        sound = QApplication.instance().core.sound

        registry = sound.registry
        current_backend = sound.backend

        list_all = all is not None and all.lower().strip() == "all"

        names = []
        statuses = []

        for backend in registry.listBackends(list_all):

            if backend is current_backend:
                status = "in use"

            elif backend.isAvailable():
                status = "available"

            else:
                status = "unavailable"

            names.append(backend.name)
            statuses.append(status)

        output = "Available sound engines:\n"
        output += format_as_table(
            columns=(names, statuses), headers=["Engine", "Status"]
        )

        world.info(output)
