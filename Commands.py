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

  def __init__( s, cmdname ):

    s.cmdname = cmdname


  def get_short_help( s ):

    if s.__doc__:
      return s.__doc__.split( u"\n" )[0]

    return None


  def get_help( s ):

    return s.__doc__


  def execute( s, world, *args ):

    if not args_match_function( s.default, [world] + list( args ) ):

      world.info( u"Invalid number of parameters for command %s." % s.cmdname )
      return

    s.default( world, *args )


  def default( s, world, *args ):

    ## Default implementation that does nothing. Overload this in subclasses.
    pass







class LoadCommand( BaseCommand ):

  ## No docstring. This is not a user-visible command.

  def default( s, world, *args ):

    world.loadFile( args and u" ".join( args ) or None )


class FindCommand( BaseCommand ):

  u"""Finds text in the output window.
  If <string> is omitted, repeat the last search."""

  def default( s, world, *args ):

    world.worldui.output_manager.findInHistory( u" ".join( args ) )


class RaiseCommand( BaseCommand ):

  ## No docstring. This is not a user-visible command.

  def default( s, world, *args ):

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


class ConnectCommand( BaseCommand ):

  u"Opens connection to the current world if it is currently closed."

  def default( s, world ):

    world.connectToWorld()


class DisconnectCommand( BaseCommand ):

  u"Closes connection to the current world."

  def default( s, world ):

    world.disconnectFromWorld()


class QuitCommand( BaseCommand ):

  u"Quits the application."

  def default( s, world ):

    singletons.mw.close()


class CloseCommand( BaseCommand ):

  u"Closes the current world."

  def default( s, world ):

    world.worldui.close()


class WorldConfSetCommand( BaseCommand ):

  u"Sets this world's given configuration key to the given value."

  def default( s, world, key, *args ):

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration variable: %s" % key )

    else:
      args = t.from_string( args )
      world.conf[ key ] = args


class ConfSetCommand( BaseCommand ):

  u"Sets the given configuration key to the given value."

  def default( s, world, key, *args ):

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration variable: %s" % key )

    else:
      args = t.from_string( args )
      singletons.config[ key ] = args


class ConfResetCommand( BaseCommand ):

  u"Resets the given configuration key to its default value."

  def default( s, world, key ):

    try:
      del singletons.config[ key ]

    except KeyError:
      pass


class WorldConfResetCommand( BaseCommand ):

  u"Resets this world's given configuration key to its global value."

  def default( s, world, key ):

    try:
      del world.conf[ key ]

    except KeyError:
      pass


class PlayCommand( BaseCommand ):

  u"Plays a sound."

  def default( s, world, filename ):

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

        tokens.append( m.group( 1 ) or m.group( 2 ) )

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

      helptxt = ""

      for cmdname in sorted( s.commands.keys() ):

        cmd  = s.lookupCommand( cmdname )
        help = cmd.get_short_help()

        if help:
          helptxt += cmdchar + u"%s" % cmdname.ljust( 18 ) + help + "\n"

      world.info( helptxt )

    else:

      cmdname = tokens[0]
      cmd = s.lookupCommand( cmdname )

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

  commands.registerCommand( "load", LoadCommand )
  commands.registerCommand( "find", FindCommand )
  commands.registerCommand( "raise", RaiseCommand )
  commands.registerCommand( "close", CloseCommand )
  commands.registerCommand( "quit", QuitCommand )
  commands.registerCommand( "connect", ConnectCommand )
  commands.registerCommand( "disconnect", DisconnectCommand )
  commands.registerCommand( "conf_set", ConfSetCommand )
  commands.registerCommand( "conf_reset", ConfResetCommand )
  commands.registerCommand( "world_conf_set", WorldConfSetCommand )
  commands.registerCommand( "world_conf_reset", WorldConfResetCommand )
  commands.registerCommand( "play", PlayCommand )
