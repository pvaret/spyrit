# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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
## FindCommand.py
##
## Command to search the output window for specific text.
##


from BaseCommand import BaseCommand


class FindCommand( BaseCommand ):

  u"""\
  Find text in the output window.

  Usage: %(cmd)s [<text>]

  If <text> is omitted, the last search is repeated.
  If <text> is a sentence containing spaces, it should be enclosed in quotes.

  Examples:
      %(cmd)s Character
      %(cmd)s "Character pages"
      %(cmd)s

  """

  def cmd( self, world, text=None ):

    world.worldui.output_manager.findInHistory( text )
