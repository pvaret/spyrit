# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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

  def __init__( self ):

    self.commands = {}


  def registerCommand( self, cmdname, command_class ):

    cmdname = cmdname.strip().lower()
    self.commands[ cmdname ] = command_class()


  ## TODO: rename this to lookup(), implement it on BaseCommand too.
  def lookupCommand( self, command ):

    return self.commands.get( command.strip().lower() )


  def parseCommand( self, cmdline ):

    cmdname, remainder = parse_command( cmdline )

    if cmdname in self.commands:
      return cmdname, cmdname, remainder

    return None, cmdname, cmdline


  def runCmdLine( self, world, cmdline ):

    cmdname, possible_cmdname, remainder = self.parseCommand( cmdline )

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

    command = self.lookupCommand( cmdname )

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



def construct_command_registry():


  from commands.HelpCommand     import HelpCommand
  from commands.SettingsCommand import SettingsCommand
  from commands.DebugCommand    import DebugCommand
  from commands.FindCommand     import FindCommand
  from commands.SessionCommand  import SessionCommand
  from commands.SoundCommand    import SoundCommand
  from commands.MatchCommand    import MatchCommand

  command_registry = CommandRegistry()

  command_registry.registerCommand( HELP,       HelpCommand )
  command_registry.registerCommand( "settings", SettingsCommand )
  command_registry.registerCommand( "debug",    DebugCommand )
  command_registry.registerCommand( "find",     FindCommand )
  command_registry.registerCommand( "session",  SessionCommand )
  command_registry.registerCommand( "sound",    SoundCommand )
  command_registry.registerCommand( "match",    MatchCommand )

  return command_registry
