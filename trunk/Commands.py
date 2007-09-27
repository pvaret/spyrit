# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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


class Commands:

  QUOTED  = re.compile( r'"(.*?)"' + '|' r"'(.*?)'" )
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

      s.world.info( "%s: no such command." % commandname )
      return

    try:
      command( *tokens )

    except TypeError:
      s.world.info( "Invalid number of parameters for command %s." \
                    % commandname )