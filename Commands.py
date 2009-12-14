# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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
## This holds the Commands class, which parses and executes command lines
## entered by the user.
##

import re

from localqt    import *

from Messages   import messages
from Singletons import singletons


class Commands:

  QUOTED  = re.compile( r'"(.*?)"' + '|' + r"'(.*?)'" )
  COMMAND = "command_"


  def __init__( s, world ):

    s.world    = world
    s.commands = {}

    ## Index the COMMAND methods for later lookup.

    for method in dir( s ):

      if not method.startswith( s.COMMAND ):
        continue

      s.commands[ method[ len( s.COMMAND ): ].lower() ] = getattr( s, method )


  def lookupCommand( s, command ):

    return s.commands[ command.strip().lower() ]


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


  def execute( s, commandline ):

    tokens = s.tokenize( commandline )

    if not tokens:
      return

    try:

      commandname = tokens.pop( 0 )
      command     = s.lookupCommand( commandname )

    except KeyError:

      s.world.info( u"%s: no such command." % commandname )
      return

    try:
      command( *tokens )

    except TypeError:
      s.world.info( u"Invalid number of parameters for command %s." \
                     % commandname )


  def command_Help( s, *args ):

    u"help <command>: Provides help on <command>."

    c = s.world.conf._input_command_char

    if not args:

      for commandname, cmd in sorted( s.commands.iteritems() ):
        doc = cmd.__doc__
        s.world.info( doc and c + doc or c + commandname )

    else:

      commandname = " ".join( args )

      try:
        cmd = s.lookupCommand( commandname )

      except KeyError:
        s.world.info( u"%s: no such command." % commandname )
        return

      doc = cmd.__doc__

      if doc:
        s.world.info( c + doc )

      else:
        s.world.info( u"No help for command %s." % commandname )


  def command_Find( s, *args ):

    u"find [<string>]: Searches for <string> in the output window." \
    u"If <string> is omitted, repeat the last search."

    s.world.worldui.output_manager.findInHistory( u" ".join( args ) )


  def command_Raise( s, *args ):

    u"raise <exception> [parameters]: Raises <exception>. " \
    u"For debugging purposes."

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


  def command_Connect( s ):

    u"connect: Opens connection to the current world if it is currently closed."

    s.world.connectToWorld()


  def command_Disconnect( s ):

    u"disconnect: Closes connection to the current world."

    s.world.disconnectFromWorld()


  def command_Quit( s ):

    u"quit: Quits the application."
    singletons.mw.close()


  def command_Close( s ):

    u"close: Closes the current world."

    s.world.worldui.close()


  def command_World_Conf_Set( s, key, *args ):

    u"world_conf_set <key> <value>: " \
    u"Sets this world's given configuration key to the given value."

    args = " ".join( args )

    t = s.world.conf.getType( key )

    if not t:
      messages.warn( u"Unknown configuration variable: %s" % key )

    else:
      args = t().from_string( args )
      s.world.conf[ key ] = args


  def command_Conf_Set( s, key, *args ):

    u"conf_set <key> <value>: " \
    u"Sets the given configuration key to the given value."

    args = " ".join( args )

    t = s.world.conf.getType( key )

    if not t:
      messages.warn( u"Unknown configuration variable: %s" % key )

    else:
      args = t().from_string( args )
      singletons.config[ key ] = args


  def command_Conf_Reset( s, key ):

    u"conf_reset <key>: " \
    u"Resets the given configuration key to its default value."

    try: del singletons.config[ key ]
    except KeyError: pass


  def command_World_Conf_Reset( s, key ):

    u"world_conf_reset <key>: " \
    u"Resets this world's given configuration key to its global value."

    try: del s.world.conf[ key ]
    except KeyError: pass


  def command_Load( s, *args ):

    s.world.loadFile( args and " ".join( args ) or None )


  def __del__( s ):

    s.commands = None
    s.world    = None
