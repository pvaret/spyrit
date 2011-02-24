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
## BaseCommand.py
##
## Abstract base class for commands.
##

from PyQt4.QtGui import QApplication

from CommandParsing import parse_command
from CommandParsing import parse_arguments
from Globals        import HELP, CMDCHAR


class BaseCommand( object ):

  ## Abstract base class for commands.

  CMD = "cmd"

  def __init__( s ):

    s.subcmds = {}

    for name in dir( s ):

      attr = getattr( s, name )

      if callable( attr ) and name.startswith( s.CMD + "_" ):
        s.subcmds[ name[ len( s.CMD + "_" ): ].lower() ] = attr


  def cmd( s, world, *args, **kwargs ):

    ## Default implementation that only displays help. Overload this in
    ## subclasses.

    commands = QApplication.instance().core.commands

    ## TODO: Clean this up; store cmd name when registering it.
    cmdname = [ k for k, v in commands.commands.iteritems()
                if v is s ][0]

    if args or kwargs:
        arg1 = ( list( args ) + kwargs.keys() )[0]
        world.info( u"Unknown argument '%s' for command %s!" \
                    % ( arg1, cmdname ) )

    world.info( u"Type '%s%s %s' for help on this command."
                % ( CMDCHAR, HELP, cmdname ) )


  def parseSubCommand( s, cmdline ):

    subcmdname, remainder = parse_command( cmdline )

    if subcmdname in s.subcmds:
      return subcmdname, subcmdname, remainder

    return None, subcmdname, cmdline


  def parseArgs( s, cmdline ):

    args, kwargs = parse_arguments( cmdline )

    return args, kwargs


  def getCallableForName( s, cmdname, subcmdname ):

    if subcmdname is None:
      return getattr( s, s.CMD, None )

    return s.subcmds.get( subcmdname.lower() )
