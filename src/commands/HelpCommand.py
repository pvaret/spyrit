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
# HelpCommand.py
#
# Implements the good old help command.
#


from textwrap import dedent

from PyQt5.QtWidgets import QApplication

from .BaseCommand import BaseCommand
from Globals import CMDCHAR
from Globals import HELP


class HelpCommand(BaseCommand):
    def cmd(self, world, cmdname=None, subcmdname=None):

        commands = QApplication.instance().core.commands

        if cmdname:

            cmd = commands.lookupCommand(cmdname)

            if not cmd:
                return self.helpNoSuchCommand(world, cmdname)

            if subcmdname:
                subcmd = cmd.getCallableForName(cmdname, subcmdname)

                if not subcmd:
                    return self.helpNoSuchCommand(world, cmdname, subcmdname)

                return self.helpCommand(world, subcmd, cmdname, subcmdname)

            return self.helpCommand(world, cmd, cmdname)

        return self.helpAll(world)

    def helpNoSuchCommand(self, world, cmdname, subcmdname=None):

        if subcmdname:
            cmdname += " " + subcmdname

        help_txt = """
        %(cmdname)s: no such command.
        Type %(CMDCHAR)s%(HELP)s for help on commands."""

        ctx = {"CMDCHAR": CMDCHAR, "cmdname": cmdname, "HELP": HELP}

        world.info(dedent(help_txt).strip() % ctx)

    def helpCommand(self, world, cmd, cmdname, subcmdname=None):

        if subcmdname:
            cmdname += " " + subcmdname

        help_txt = self.get_help(cmd)

        if not help_txt:
            world.info("No help on command '%s'." % cmdname)
            return

        cmd = CMDCHAR + cmdname

        ctx = {"CMDCHAR": CMDCHAR, "cmdname": cmdname, "cmd": cmd, "HELP": HELP}

        help_txt = "Help on '%(CMDCHAR)s%(cmdname)s':\n" + help_txt
        world.info(help_txt % ctx)

    def get_short_help(self, cmd):

        if cmd.__doc__:
            return cmd.__doc__.split("\n")[0].strip()

        return None

    def get_help(self, cmd):

        if not cmd.__doc__:
            return None

        doc = dedent(cmd.__doc__)

        if not hasattr(cmd, "subcmds") or len(cmd.subcmds) == 0:
            return doc

        helptxt = [doc]
        helptxt += [""]
        helptxt += ["Subcommands:"]

        ljust = max(len(c) for c in cmd.subcmds.keys()) + 2

        for subcmdname, subcmd in sorted(cmd.subcmds.items()):

            doc = subcmd.__doc__

            if doc:
                line = (
                    "  %s " % (subcmdname.ljust(ljust))
                    + doc.split("\n")[0].strip()
                )
                helptxt.append(line)

        helptxt += [""]
        helptxt += [
            "Type '/help COMMAND SUBCOMMAND' for specific help on a "
            "subcommand."
        ]

        return "\n".join(helptxt)

    def helpAll(self, world):

        helptxt = ["Available commands:\n"]

        cmd_registry = QApplication.instance().core.commands

        ljust = max(len(c) for c in cmd_registry.commands.keys()) + 2

        for cmdname in sorted(cmd_registry.commands.keys()):

            cmd = cmd_registry.lookupCommand(cmdname)
            help = self.get_short_help(cmd)

            if help:
                helptxt.append(CMDCHAR + "%s" % cmdname.ljust(ljust) + help)

        helptxt += [""]
        helptxt += [
            "Type '%shelp COMMAND' for more help on a command." % CMDCHAR
        ]

        world.info("\n".join(helptxt))
