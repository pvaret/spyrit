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


import inspect


def args_match_function( func, args ):

  f_args, varargs, varkw, defaults = inspect.getargspec( func )

  n_args  = len( args )
  n_fargs = len( f_args )

  n_defaults = len( defaults ) if defaults else 0

  if inspect.ismethod( func ):
    n_fargs -= 1  ## Account for implicit self argument.

  if n_args < n_fargs - n_defaults:
    ## Not enough arguments were given to the function.
    return False

  if varargs is not None:
    ## Function declaration bears a *args clause, so any number of arguments
    ## will do.
    return True

  return ( n_fargs - n_defaults <= n_args <= n_fargs )





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



