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

from CommandParsing import parse_cmdline


def match_args_to_function( func, args, kwargs ):

  f_args, f_varargs, f_varkw, f_defaults = inspect.getargspec( func )

  ## 1/ Compute the function's natural args and kwargs:

  if f_defaults:
    f_kwargs = dict( zip( f_args[ -len( f_defaults ): ], f_defaults ) )
    f_args   = f_args[ :-len( f_defaults ) ]

  else:
    f_kwargs = {}

  ## 2/ Match call kwargs to function kwargs:

  if inspect.ismethod( func ):
    ## Account for implicit self argument in methods.
    args.insert( 0, 'self' )

  for kwarg in kwargs:

    if kwarg in f_kwargs:
      del f_kwargs[ kwarg ]

    elif not f_varkw:
      ## Function called with a kwarg that isn't in its definition, and
      ## function doesn't have a generic **kwargs to fallback to:
      return False, u"%s: unknown parameter!" % kwarg

  ## 3/ Match remaining call args to remaining function args.

  if len( args ) < len( f_args ):
    return False, u"Too few parameters!"

  if len( args ) > len( f_args ) + len( f_kwargs ) and not f_varargs:
    return False, u"Too many parameters!"

  return True, None





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


  #def execute( s, world, subcmd, args, kwargs ):

  #  cmd = s.subcmds.get( subcmd, getattr( s, s.CMD ) )

  #  matching, errmsg = match_args_to_function( cmd, [world] + args, kwargs )

  #  if not matching:
  #    world.info( errmsg )
  #    return

  #  cmd( world, *args, **kwargs )


  #def cmd( s, world, *args, **kwargs ):

  #  ## Default implementation that does nothing. Overload this in subclasses.
  #  pass


  def parseSubCommand( s, cmdline ):

    _, subcmd, _, _ = parse_cmdline( cmdline )

    if subcmd in s.subcmds:
      return subcmd

    return None


  def parseArgs( s, cmdline ):

    _, _, args, kwargs = parse_cmdline( cmdline )

    return args, kwargs


  def getCallableByName( s, cmd, subcmd=None ):

    if subcmd is None:
      return getattr( s, s.CMD, None )

    return s.subcmds.get( subcmd.lower() )
