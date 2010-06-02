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


  def cmd_ifmatch( s, world, matchgroup, action, *args, **kwargs ):

    u"Add action to be taken when a line matches the given group."

    action = world.socketpipeline.triggersmanager.loadAction( action, args, kwargs )

    if action:
      world.socketpipeline.triggersmanager.addAction( action, matchgroup )


  def cmd_list( s, world ):

    u"List all matches and the related actions."

    msg = []
    tm  = world.socketpipeline.triggersmanager

    msg.append( u"Matches:" )

    if tm.isEmpty():
      msg.append( u"  None." )

    for group in sorted( tm.matches.iterkeys() ):

      groupname = u"[%s] " % group
      indent    = len( groupname )

      for i, m in enumerate( tm.matches[ group ] ):
        if i == 0:
          prefix = groupname
        else:
          prefix = u" " * indent

        msg.append( prefix + unicode( m ) )

      actions = tm.actions.get( group, [] )

      for i, a in enumerate( actions ):

        if i == 0:
          prefix = u" " * indent + unichr( 0x2192 ) + " "
        else:
          prefix = u" " * ( indent + 2 )

        msg.append( prefix + unicode( a ) )

    world.info( u"\n".join( msg ) )
