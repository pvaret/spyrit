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
## BaseCommand.py
##
## Abstract base class for commands.
##


from PyQt5.QtWidgets import QApplication

from .CommandParsing import parse_command
from .CommandParsing import parse_arguments
from Globals import HELP, CMDCHAR


class BaseCommand:

    ## Abstract base class for commands.

    CMD = "cmd"

    def __init__(self):

        self.subcmds = {}

        for name in dir(self):

            attr = getattr(self, name)

            if callable(attr) and name.startswith(self.CMD + "_"):
                self.subcmds[name[len(self.CMD + "_") :].lower()] = attr

    def cmd(self, world, *args, **kwargs):

        ## Default implementation that only displays help. Overload this in
        ## subclasses.

        commands = QApplication.instance().core.commands

        ## TODO: Clean this up; store cmd name when registering it.
        cmdname = [k for k, v in commands.commands.items() if v is self][0]

        if args or kwargs:
            arg1 = (list(args) + list(kwargs.keys()))[0]
            world.info(
                "Unknown argument '%s' for command %s!" % (arg1, cmdname)
            )

        world.info(
            "Type '%s%s %s' for help on this command."
            % (CMDCHAR, HELP, cmdname)
        )

    def parseSubCommand(self, cmdline):

        subcmdname, remainder = parse_command(cmdline)

        if subcmdname in self.subcmds:
            return subcmdname, subcmdname, remainder

        return None, subcmdname, cmdline

    def parseArgs(self, cmdline):

        args, kwargs = parse_arguments(cmdline)

        return args, kwargs

    def getCallableForName(self, cmdname, subcmdname):

        if subcmdname is None:
            return getattr(self, self.CMD, None)

        return self.subcmds.get(subcmdname.lower())
