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
# DebugCommands.py
#
# Debugging-related command.
#

import builtins

from .BaseCommand import BaseCommand


class DebugCommand(BaseCommand):

    # No docstring. This is not a user-visible command.

    def cmd_raise(self, _, *args: str) -> None:

        # No docstring. This is not a user-visible subcommand.

        e = None

        if args:

            exc = getattr(builtins, args[0], Exception)

            try:
                is_an_exception = issubclass(exc, BaseException)

            except TypeError:  # exc is not a class!
                is_an_exception = False

            if is_an_exception:
                e = exc(*args[1:])

        if not e:
            e = Exception(args and " ".join(args) or None)

        raise e

    def cmd_execute(self, world, filename):

        # No docstring. This is not a user-visible subcommand.

        f = world.openFileOrErr(filename)

        if not f:
            return

        exec(f.read())  # nosec - tell bandit we know this is unsafe.

    def cmd_load(self, world, filename=None, blocksize=None):

        # No docstring. This is not a user-visible subcommand.

        if blocksize is not None and not blocksize.isdigit():
            blocksize = None

        kwargs = {}

        if filename:
            kwargs["filename"] = filename

        if blocksize:
            kwargs["blocksize"] = int(blocksize)

        world.loadFile(**kwargs)
