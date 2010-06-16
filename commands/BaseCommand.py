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
## BaseCommand.py
##
## Abstract base class for commands.
##


from CommandParsing import parse_command
from CommandParsing import parse_arguments



class BaseCommand( object ):

  ## Abstract base class for commands.

  CMD = "cmd"

  def __init__( s ):

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


  def cmd( s, world, *args, **kwargs ):

    ## Default implementation that only displays help. Overload this in
    ## subclasses.

    world.info( s.get_help() )


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
