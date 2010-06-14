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
## CommandRegistry.py
##
## This holds the command registry that knows about commands, parses their
## arguments, retrieves their help and dispatches their calls.
##


from Globals                 import CMDCHAR
from commands.CommandParsing import parse_cmdline

from textwrap import dedent


class CommandRegistry:

  HELP = "help"

  def __init__( s ):

    s.commands = {}


  def registerCommand( s, cmdname, command_class ):

    cmdname = cmdname.strip().lower()
    s.commands[ cmdname ] = command_class()


  def lookupCommand( s, command ):

    return s.commands.get( command.strip().lower() )


  def execute( s, world, cmdline ):

    cmdname, _, _, _ = parse_cmdline( cmdline )

    if cmdname is None:
      return

    command = s.lookupCommand( cmdname )

    if not command:

      help_txt = u"""%(cmdname)s: no such command.
                 Type %(CMDCHAR)shelp for a list of available commands."""

      world.info( dedent( help_txt ) \
                 % { 'cmdname': cmdname, 'CMDCHAR': CMDCHAR } )
      return

    remainder = cmdline[ len( cmdname ): ].lstrip()
    context   = { 'cmdname': cmdname }

    context, remainder = command.parseSubCommand( context, remainder )
    context            = command.parseArgs( context, remainder )
    cmd_callable       = command.getCallableFromParseContext( context )

    if cmd_callable is None:  ## Command not found!

      complete_cmdname = cmdname
      subcmdname = context.get( 'possible_subcmdname' )

      if subcmdname:
        complete_cmdname += " " + subcmdname

      help_txt = u"""\
          %(complete_cmdname)s: no such command.
          Type %(CMDCHAR)shelp %(cmdname)s for help on this command."""

      world.info( dedent( help_txt ) \
                  % { 'complete_cmdname': complete_cmdname,
                      'cmdname': cmdname,
                      'CMDCHAR': CMDCHAR } )
      return

    args   = context.get( 'args',   [] )
    kwargs = context.get( 'kwargs', {} )

    ## TODO: Pass this to an executor that handles errors safely.
    return cmd_callable( world, *args, **kwargs )


  def doHelp( s, world, tokens ):

    tokens = tokens[ 1: ]

    ##XXX Improve whole help handling!

    if not tokens:  ## Default help text.

      helptxt = [ "Available commands:\n" ]

      ljust = max( len( c ) for c in s.commands.keys() ) + 2

      for cmdname in sorted( s.commands.keys() ):

        cmd  = s.lookupCommand( cmdname )
        help = cmd.get_short_help()

        if help:
          helptxt.append( CMDCHAR + u"%s" % cmdname.ljust( ljust ) + help )

      helptxt += [ "" ]
      helptxt += [ "Type '%shelp COMMAND' for more help on a command."
                   % CMDCHAR ]

      world.info( u'\n'.join( helptxt ) )

    else:  ## Help on a specific command.

      cmdname = tokens[0]
      cmd     = s.lookupCommand( cmdname )

      if not cmd:
        world.info( "No such command: %s" % cmdname )

      else:

        help = cmd.get_help()

        if not help:
          world.info( "No help for command %s. " \
                      "(Command reserved for internal use.)" % cmdname )
        else:
          world.info( CMDCHAR + u"%s " % cmdname + "\n  " + help )


  def __del__( s ):

    s.commands = None



## Offer a function to register our local commands:

def register_local_commands( commands ):

  from commands.ConfCommand    import ConfCommand
  from commands.DebugCommand   import DebugCommand
  from commands.OutputCommand  import OutputCommand
  from commands.SessionCommand import SessionCommand
  from commands.SoundCommand   import SoundCommand
  from commands.MatchCommand   import MatchCommand

  commands.registerCommand( "conf",    ConfCommand )
  commands.registerCommand( "debug",   DebugCommand )
  commands.registerCommand( "output",  OutputCommand )
  commands.registerCommand( "session", SessionCommand )
  commands.registerCommand( "sound",   SoundCommand )
  commands.registerCommand( "match",   MatchCommand )
