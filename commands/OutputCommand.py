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
## OutputCommand.py
##
## Command to manage the world's output.
##


from BaseCommand import BaseCommand


class OutputCommand( BaseCommand ):

  u"""Manage the output window."""

  def cmd_load( s, world, *args ):

    ## No docstring. This is not a user-visible subcommand.

    world.loadFile( args and u" ".join( args ) or None )


  def cmd_find( s, world, *args ):

    u"""Finds the given text in the output window.
    If <string> is omitted, repeat the last search."""

    world.worldui.output_manager.findInHistory( u" ".join( args ) )
