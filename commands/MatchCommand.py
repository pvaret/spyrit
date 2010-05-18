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
## MatchCommand.py
##
## Commands to manage matches.
##


from BaseCommand import BaseCommand


class MatchCommand( BaseCommand ):

  u"Create, list, delete match patterns."

  def cmd_add( s, world, match ):

    u"Add a new match pattern."

    world.socketpipeline.triggersmanager.addMatch( match )


  def cmd_del( s, world, matchgroup ):

    u"Delete the given match group."

    world.socketpipeline.triggersmanager.delGroup( matchgroup )
