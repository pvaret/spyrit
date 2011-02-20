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
## HelpCommand.py
##
## Implements the good old help command.
##


from textwrap import dedent

from localqt import *

from BaseCommand import BaseCommand
from Globals     import CMDCHAR
from Globals     import HELP



class HelpCommand( BaseCommand ):

  def cmd( s, world, cmdname=None, subcmdname=None ):

    commands = qApp().core.command

    if cmdname:

      cmd = commands.lookupCommand( cmdname )

      if not cmd:
        return s.helpNoSuchCommand( world, cmdname )

      if subcmdname:
        subcmd = cmd.getCallableForName( cmdname, subcmdname )

        if not subcmd:
          return s.helpNoSuchCommand( world, cmdname, subcmdname )

        return s.helpCommand( world, subcmd, cmdname, subcmdname )

      return s.helpCommand( world, cmd, cmdname )

    return s.helpAll( world )


  def helpNoSuchCommand( s, world, cmdname, subcmdname=None ):

    if subcmdname:
      cmdname += " " + subcmdname

    help_txt = u"""\
        %(cmdname)s: no such command.
        Type %(CMDCHAR)s%(HELP)s for help on commands."""

    ctx = { 'CMDCHAR': CMDCHAR,
            'cmdname': cmdname,
            'HELP': HELP }

    world.info( dedent( help_txt ) % ctx )


  def helpCommand( s, world, cmd, cmdname, subcmdname=None ):

    if subcmdname:
      cmdname += " " + subcmdname

    help_txt = s.get_help( cmd )

    if not help_txt:
      world.info( u"No help on command '%s'." % cmdname  )
      return

    cmd = CMDCHAR + cmdname

    ctx = { 'CMDCHAR': CMDCHAR,
            'cmdname': cmdname,
            'cmd':     cmd,
            'HELP':    HELP }

    help_txt = u"Help on '%(CMDCHAR)s%(cmdname)s':\n" + help_txt
    world.info( help_txt % ctx )


  def get_short_help( s, cmd ):

    if cmd.__doc__:
      return cmd.__doc__.split( u"\n" )[0].strip()

    return None


  def get_help( s, cmd ):

    if not cmd.__doc__:
      return None

    doc = dedent( cmd.__doc__ )

    if not hasattr( cmd, 'subcmds' ) or len( cmd.subcmds ) == 0:
      return doc

    helptxt  = [ doc ]
    helptxt += [ u"" ]
    helptxt += [ u"Subcommands:" ]

    ljust = max( len( c ) for c in cmd.subcmds.keys() ) + 2

    for subcmdname, subcmd in sorted( cmd.subcmds.iteritems() ):

      doc = subcmd.__doc__

      if doc:
        line = ( "  %s " % ( subcmdname.ljust( ljust ) )
               + doc.split( u"\n" )[0].strip() )
        helptxt.append( line )

    helptxt += [ u"" ]
    helptxt += [ u"Type '/help COMMAND SUBCOMMAND' for specific help on a " \
                  "subcommand." ]

    return u"\n".join( helptxt )


  def helpAll( s, world ):

    helptxt = [ "Available commands:\n" ]

    cmd_registry = qApp().core.commands

    ljust = max( len( c ) for c in cmd_registry.commands.keys() ) + 2

    for cmdname in sorted( cmd_registry.commands.keys() ):

      cmd  = cmd_registry.lookupCommand( cmdname )
      help = s.get_short_help( cmd )

      if help:
        helptxt.append( CMDCHAR + u"%s" % cmdname.ljust( ljust ) + help )

    helptxt += [ u"" ]
    helptxt += [ u"Type '%shelp COMMAND' for more help on a command."
                 % CMDCHAR ]

    world.info( u'\n'.join( helptxt ) )
