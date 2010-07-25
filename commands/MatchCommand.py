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


from Matches     import MatchCreationError
from BaseCommand import BaseCommand
from Globals     import LEFTARROW


class MatchCommand( BaseCommand ):

  u"""Create, list, delete match patterns."""

  def cmd_add( s, world, pattern, group=None, type=u"smart" ):

    u"""\
    Add a new match pattern.

    Usage: %(cmd)s <pattern> [<group>] [type="smart"|"regex"]

    The <group> parameter lets you specify the name of a group for the match,
    so patterns with the same semantics and on which the same action must be
    taken when a match is found, can be put together.

    If the given group doesn't already exist, it will be automatically created.
    If the parameter is left unspecified, the command creates a new group using
    the next available ordinal number as its name, i.e. '1', '2', '3'...

    The <type> parameter allows you to choose the syntax for the pattern:
    'smart' or 'regex'. If unspecified, the default is 'smart'.

    'smart' is a very simple pattern syntax:
        '*' matches anything, as many characters as it can;
        '%%' matches anything, as few characters as it can;
        '[<token>]' matches anything as token <token>.
    The characters '*', '%%', '[' and ']' can be escaped with a backslash.

    'regex' follows the usual syntax of regular expressions:
        http://docs.python.org/library/re.html
    Named regular expression groups are used as the pattern's tokens.

    Tokens can be used by other commands to single out parts of the match to
    highlight or otherwise act upon.

    Don't forget to quote the pattern if it contains spaces!

    Examples:
        %(cmd)s "You have received a message from *"
        %(cmd)s "[player] pages: [message]" group=pages
        %(cmd)s "From afar, (?P<player>\w+) pages (?P<message>.+)" group=pages type=regex

    """

    mgr = world.socketpipeline.triggersmanager

    try:
      match = mgr.createMatch( pattern, type )

    except MatchCreationError, e:
      world.info( unicode( e ) )
      return

    mgr.addMatch( match, group )
    world.info( u"Match added." )


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
          prefix = u" " * indent + LEFTARROW + " "
        else:
          prefix = u" " * ( indent + 2 )

        msg.append( prefix + unicode( a ) )

    world.info( u"\n".join( msg ) )
