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
## CommandExecutor.py
##
## Provides helpers to safely run arbitrary callables with arbitrary argument
## sets.
##


import inspect


class ExecuteError( RuntimeError ):
  pass


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
    f_args.pop( 0 )

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

    if len( args ) > 2:
      msg = u"Too many parameters! (Did you forget some quotation marks?)"

    else:
      msg = u"Too many parameters!"

    return False, msg

  return True, None


def execute( func, args, kwargs ):

  ok, errmsg = match_args_to_function( func, args, kwargs )

  if not ok:
    raise ExecuteError( errmsg )

  try:
    return func( *args, **kwargs )

  except Exception, e:
    raise ExecuteError( unicode( e ) )
