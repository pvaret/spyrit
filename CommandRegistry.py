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


import re


class CommandRegistry:

  QUOTED = re.compile( r'"(.*?)"' + '|' + r"'(.*?)'" )
  HELP   = "help"

  def __init__( s ):

    s.commands = {}


  def registerCommand( s, cmdname, command_class ):

    cmdname = cmdname.strip().lower()
    s.commands[ cmdname ] = command_class( cmdname )


  def lookupCommand( s, command ):

    return s.commands.get( command.strip().lower() )


  def tokenize( s, line ):

    ## Turns a line such as 'A B C "D E" F' into [ 'A', 'B', 'C', 'D E', 'F' ]

    line   = line.strip()
    tokens = []

    while True:

      m = s.QUOTED.search( line )

      if m:

        for token in line[ 0:m.start() ].split():
          tokens.append( token.strip() )

        token = m.group( 1 ) if m.group( 1 ) is not None else m.group( 2 )
        tokens.append( token )

        line = line[ m.end(): ]

      else:

        for token in line.split():
          tokens.append( token.strip() )

        break

    return tokens


  def execute( s, world, cmdline ):

    tokens = s.tokenize( cmdline )

    if not tokens:
      return

    cmdname = tokens.pop( 0 )

    if cmdname == s.HELP:

      s.doHelp( world, *tokens )
      return

    command = s.lookupCommand( cmdname )

    if not command:

      world.info( u"%s: no such command." % cmdname )
      return

    command.execute( world, *tokens )


  def doHelp( s, world, *tokens ):

    cmdchar = world.conf._input_command_char

    if not tokens:  ## Default help text.

      helptxt = [ "Available commands:\n" ]

      ljust = max( len( c ) for c in s.commands.keys() ) + 2

      for cmdname in sorted( s.commands.keys() ):

        cmd  = s.lookupCommand( cmdname )
        help = cmd.get_short_help()

        if help:
          helptxt.append( cmdchar + u"%s" % cmdname.ljust( ljust ) + help )

      helptxt += [ "" ]
      helptxt += [ "Type '%shelp COMMAND' for more help on a command."
                   % cmdchar ]

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
          world.info( cmdchar + u"%s " % cmdname + "\n  " + help )


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