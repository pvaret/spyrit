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
## Commands.py
##
## This holds the command-related classes, in particular CommandRegistry and
## BaseCommand, and the subclasses of the latter. Together they provide the
## use with a way to perform operations from the input box.
##

import re
import inspect

from localqt    import *

from Messages   import messages
from Singletons import singletons





def args_match_function( func, args ):

  f_args, varargs, varkw, defaults = inspect.getargspec( func )

  n_args  = len( args )
  n_fargs = len( f_args )

  if inspect.ismethod( func ):
    n_fargs -= 1  ## Account for implicit self argument.

  if n_args < n_fargs:
    ## Not enough arguments were given to the function.
    return False

  if varargs is not None:
    ## Function declaration bears a *args clause, so any number of arguments
    ## will do.
    return True

  return ( n_args == n_fargs )









## Actual command implementation.


class BaseCommand( object ):

  ## Abstract base class for commands.

  CMD = "cmd"

  def __init__( s, cmdname ):

    s.cmdname = cmdname
    s.subcmds = {}

    for name in dir( s ):

      attr = getattr( s, name )

      if callable( attr ) and name.startswith( s.CMD + "_" ):
        s.subcmds[ name[ len( s.CMD + "_" ): ].lower() ] = attr


  def get_short_help( s ):

    if s.__doc__:
      return s.__doc__.split( u"\n" )[0].strip()

    return None


  def get_help( s ):

    if not s.__doc__:
      return None

    doc = s.__doc__.strip()

    if not s.subcmds:
      return doc

    helptxt  = [ doc ]
    helptxt += [ u"" ]
    helptxt += [ u"Subcommands:" ]

    ljust = max( len( c ) for c in s.subcmds.keys() ) + 2

    for cmdname, cmd in sorted( s.subcmds.iteritems() ):

      doc = cmd.__doc__

      if doc:
        line = ( "  %s " % ( cmdname.ljust( ljust ) )
               + doc.split( u"\n" )[0].strip() )
        helptxt.append( line )

    return u"\n".join( helptxt )


  def get_cmd_and_args( s, args ):

    if len( args ) == 0:
      return ( getattr( s, s.CMD ), args )

    possible_subcmd = args[ 0 ].lower()

    if possible_subcmd in s.subcmds:
      return ( s.subcmds[ possible_subcmd ], args[ 1: ] )

    return ( getattr( s, s.CMD ), args )


  def execute( s, world, *args ):

    cmd, args = s.get_cmd_and_args( args )

    if not args_match_function( cmd, [world] + list( args ) ):

      world.info( u"Invalid number of parameters." )
      return

    cmd( world, *args )


  def cmd( s, world, *args ):

    ## Default implementation that does nothing. Overload this in subclasses.
    pass




## Implementation of commands.


class OutputCommand( BaseCommand ):

  u"""Manage the output window."""

  def cmd_load( s, world, *args ):

    ## No docstring. This is not a user-visible subcommand.

    world.loadFile( args and u" ".join( args ) or None )


  def cmd_find( s, world, *args ):

    u"""Finds the given text in the output window.
    If <string> is omitted, repeat the last search."""

    world.worldui.output_manager.findInHistory( u" ".join( args ) )


class DebugCommand( BaseCommand ):

  ## No docstring. This is not a user-visible command.

  def cmd_raise( s, world, *args ):

    if args:

      parent_exception = __builtins__.get( "BaseException", Exception )

      exc = __builtins__.get( args[0], None )

      try:
        is_an_exception = issubclass( exc, parent_exception )

      except TypeError:
        is_an_exception = False

      if is_an_exception:

        raise exc( *args[1:] )
        return

    raise Exception( args and " ".join( args ) or None )


class SessionCommand( BaseCommand ):

  u"""Connect, disconnect, close, quit."""

  def cmd_connect( s, world ):

    u"Opens connection to the current world if it is currently closed."

    world.connectToWorld()


  def cmd_disconnect( s, world ):

    u"Closes connection to the current world."

    world.disconnectFromWorld()


  def cmd_quit( s, world ):

    u"Quits the application."

    singletons.mw.close()


  def cmd_close( s, world ):

    u"Closes the current world."

    world.worldui.close()



class ConfCommand( BaseCommand ):

  u"Configure the application."

  def cmd_set( s, world, key, *args ):

    u"Sets given configuration key to the given value globally."

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )

    else:
      args = t.from_string( args )
      singletons.config[ key ] = args


  def cmd_worldset( s, world, key, *args ):

    u"Sets given configuration key to the given value for this world."

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )

    else:
      args = t.from_string( args )
      world.conf[ key ] = args


  def cmd_reset( s, world, key ):

    u"Resets the given configuration key to its default value."

    try:
      del singletons.config[ key ]

    except KeyError:
      pass


  def cmd_worldreset( s, world, key ):

    u"Resets the given configuration key for this world to its global value."

    try:
      del world.conf[ key ]

    except KeyError:
      pass



class SoundCommand( BaseCommand ):

  u"Sound-related operations."

  def cmd_play( s, world, filename ):

    u"Play a sound."

    singletons.sound.play( filename )



## Implementation of command registry.

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

  commands.registerCommand( "output",  OutputCommand )
  commands.registerCommand( "debug",   DebugCommand )
  commands.registerCommand( "session", SessionCommand )
  commands.registerCommand( "conf",    ConfCommand )
  commands.registerCommand( "sound",   SoundCommand )
