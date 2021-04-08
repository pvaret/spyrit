# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## SessionCommand.py
##
## Commands to manage the session's state.
##


from PyQt5.QtWidgets import QApplication

from .BaseCommand import BaseCommand


class SessionCommand(BaseCommand):

    ## TODO: Maybe split this out into several commands. Those don't feel like
    ## they belong together. So for now we hide the docstring so the commands
    ## will remain hidden in the help.
    """Connect, disconnect, close, quit."""

    def cmd_reconnect(self, world):

        """
        Reconnect to the current world if it is currently disconnected.

        Usage: %(cmd)s

        """

        world.connectToWorld()

    def cmd_disconnect(self, world):

        """
        Disconnect from the current world.

        Usage: %(cmd)s

        """

        world.disconnectFromWorld()

    def cmd_quit(self, world):

        """
        Quit the application.

        Usage: %(cmd)s

        """

        QApplication.instance().closeAllWindows()

    def cmd_close(self, world):

        """
        Closes the current tab.

        Usage: %(cmd)s

        """

        world.worldui.close()
