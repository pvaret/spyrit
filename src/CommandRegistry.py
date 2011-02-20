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
## CommandRegistry.py
##
## This holds the command registry that knows about commands and how to run
## them.
##


from Globals                  import CMDCHAR
from Globals                  import HELP
from commands.CommandParsing  import parse_command
from commands.CommandExecutor import execute
from commands.CommandExecutor import ExecuteError

from textwrap import dedent



class CommandRegistry:

  def __init__( s ):

    s.commands = {}


  def registerCommand( s, cmdname, command_class ):

    cmdname = cmdname.strip().lower()
    s.commands[ cmdname ] = command_class()


  ## TODO: rename this to lookup(), implement it on BaseCommand too.
  def lookupCommand( s, command ):

    return s.commands.get( command.strip().lower() )


  def parseCommand( s, cmdline ):

    cmdname, remainder = parse_command( cmdline )

    if cmdname in s.commands:
      return cmdname, cmdname, remainder

    return None, cmdname, cmdline


  def runCmdLine( s, world, cmdline ):

    cmdname, possible_cmdname, remainder = s.parseCommand( cmdline )

    if not possible_cmdname:  ## Empty command line. Do nothing.
      return

    if not cmdname:  ## Command not found.

      help_txt = u"""\
                 %(possible_cmdname)s: no such command.
                 Type %(CMDCHAR)s%(HELP)s for a list of available commands."""

      ctx = { 'possible_cmdname': possible_cmdname,
              'CMDCHAR': CMDCHAR,
              'HELP': HELP }
      world.info( dedent( help_txt ) % ctx )
      return

    command = s.lookupCommand( cmdname )

    subcmdname, possible_subcmdname, remainder = command.parseSubCommand( remainder )

    args, kwargs = command.parseArgs( remainder )
    cmd_callable = command.getCallableForName( cmdname, subcmdname )

    if cmd_callable is None:  ## Command not found!

      complete_cmdname = cmdname

      if possible_subcmdname:
        cmdname +=  " " + possible_subcmdname

      help_txt = u"""\
          %(complete_cmdname)s: no such command.
          Type %(CMDCHAR)s%(HELP)s %(cmdname)s for help on this command."""

      ctx = { 'complete_cmdname': complete_cmdname,
              'CMDCHAR': CMDCHAR,
              'cmdname': cmdname,
              'HELP': HELP }
      world.info( dedent( help_txt ) % ctx )
      return

    args.insert( 0, world )

    try:
      return execute( cmd_callable, args, kwargs )

    except ExecuteError, e:
      msg = u"Command error: %s"
      world.info( msg % e )


  def __del__( s ):

    s.commands = None



def construct_command_registry():


  from commands.HelpCommand    import HelpCommand
  from commands.ConfCommand    import ConfCommand
  from commands.DebugCommand   import DebugCommand
  from commands.FindCommand    import FindCommand
  from commands.SessionCommand import SessionCommand
  from commands.SoundCommand   import SoundCommand
  from commands.MatchCommand   import MatchCommand

  command_registry = CommandRegistry()

  command_registry.registerCommand( HELP,      HelpCommand )
  command_registry.registerCommand( "conf",    ConfCommand )
  command_registry.registerCommand( "debug",   DebugCommand )
  command_registry.registerCommand( "find",    FindCommand )
  command_registry.registerCommand( "session", SessionCommand )
  command_registry.registerCommand( "sound",   SoundCommand )
  command_registry.registerCommand( "match",   MatchCommand )

  return command_registry
