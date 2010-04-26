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
## SessionCommand.py
##
## Commands to manage the session's state.
##


from BaseCommand import BaseCommand
from Singletons  import singletons


class SessionCommand( BaseCommand ):

  u"""Connect, disconnect, close, quit."""

  def cmd_connect( s, world ):

    u"Opens connection to the current world if it is currently closed."

    world.connectToWorld()


  def cmd_disconnect( s, world ):

    u"Closes connection to the current world."

    world.disconnectFromWorld()


  def cmd_quit( s, world ):

    u"Quits the application."

    singletons.mw.close()


  def cmd_close( s, world ):

    u"Closes the current world."

    world.worldui.close()

