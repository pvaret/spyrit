# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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
## DebugCommands.py
##
## Debugging-related command.
##


from BaseCommand import BaseCommand


class DebugCommand( BaseCommand ):

  ## No docstring. This is not a user-visible command.

  def cmd_raise( s, world, *args ):

    e = None

    if args:

      parent_exception = __builtins__.get( "BaseException", Exception )
      exc = __builtins__.get( args[0], None )

      try:
        is_an_exception = issubclass( exc, parent_exception )

      except TypeError:
        is_an_exception = False

      if is_an_exception:
        e = exc( *args[1:] )

    if not e:
      e = Exception( args and " ".join( args ) or None )

    e.do_not_catch = True

    raise e


  def cmd_execute( s, world, filename ):

      f = world.openFileOrErr( filename )

      if not f:
        return

      exec f.read()
