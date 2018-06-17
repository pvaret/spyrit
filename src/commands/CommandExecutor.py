# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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

u"""\

:doctest:

>>> from commands.CommandExecutor import *

"""

import inspect


class ExecuteError( RuntimeError ):
  pass




def match_args_to_function( callable, provided_args, provided_kwargs ):

  u"""\
  Check that the given arguments fit the given callable's spec.

  Given a few simple functions:

  >>> def simple( a, b=None ):
  ...   pass
  >>> def simple_args( a, b=None, *args ):
  ...   pass
  >>> def simple_kwargs( a, b=None, **kwargs ):
  ...   pass

  Let us see how it works:

  >>> ok, msg = match_args_to_function( simple, ( 'a', 'b' ), {} )
  >>> print ok
  True

  >>> ok, msg = match_args_to_function( simple, ( 'a', ), {} )
  >>> print ok
  True

  >>> ok, msg = match_args_to_function( simple, (), {} )
  >>> print ok  ## Missing argument a!
  False

  >>> ok, msg = match_args_to_function( simple, (), { 'a': 1 } )
  >>> print ok  ## Passing kwargs also works.
  True

  >>> ok, msg = match_args_to_function( simple, ( 'a' ), { 'c': 1 } )
  >>> print ok  ## Passing an unexpected argument doesn't, though.
  False

  >>> ok, msg = match_args_to_function( simple, ( 'a' ), { 'a': 1 } )
  >>> print ok  ## Neither does passing an already provided argument.
  False

  >>> ok, msg = match_args_to_function( simple, ( 'a', 'b', 'c' ), {} )
  >>> print ok  ## And neither does passing too many arguments.
  False

  >>> ok, msg = match_args_to_function( simple_args, ( 'a', 'b', 'c' ), {} )
  >>> print ok  ## Unless the function accepts *args.
  True

  >>> ok, msg = match_args_to_function( simple_kwargs, ( 'a', 'b' ), { 'c': 1 } )
  >>> print ok  ## Or the function accepts **kwargs.
  True

  Class instantiations and method calls also work:

  >>> class A1:
  ...   pass

  >>> class A2:
  ...   def __init__( self, a ):
  ...     pass
  ...   def method( self, a ):
  ...     pass
  ...   @classmethod
  ...   def classmethod( cls, a ):
  ...     pass
  ...   @staticmethod
  ...   def staticmethod( a ):
  ...     pass

  >>> ok, msg = match_args_to_function( A1, (), {} )
  >>> print ok  ## It works even with no __init__ method defined.
  True

  >>> ok, msg = match_args_to_function( A2, ( 'a' ), {} )
  >>> print ok  ## If __init__ exists, its spec is used.
  True

  >>> a = A2( 'a' )

  >>> ok, msg = match_args_to_function( a.method, ( 'a' ), {} )
  >>> print ok  ## Instance methods work like you'd expect.
  True

  >>> ok, msg = match_args_to_function( a.classmethod, ( 'a' ), {} )
  >>> print ok  ## But so do class methods.
  True

  >>> ok, msg = match_args_to_function( a.staticmethod, ( 'a' ), {} )
  >>> print ok  ## And static methods.
  True

  """

  ## When a class is called, the actual method invoked is __init__. The
  ## downside of this approach: this function fails if the class doesn't bear
  ## an __init__ method, or if its __init__ method is a C builtin. Be careful.

  if inspect.isclass( callable ):

    ## When a class is instantiated, what's really called is its __init__
    ## method. If there is no such method, use a null function instead.
    callable = getattr( callable, "__init__", lambda: None )

  expected_args, star_args, star_kwargs, defaults = \
                                           inspect.getargspec( callable )

  ## Reminder:
  ##   - expected_args is the list of the callable's arguments.
  ##   - defaults is a tuple of default arguments.
  ##   - star_args and star_kwargs are the names of the * and ** arguments
  ##     (usually 'args' and 'kwargs').

  ## Account for implicit 'self' argument in methods:
  if inspect.ismethod( callable ):
    expected_args.pop( 0 )

  actual_args = {}
  actual_star_args = []
  actual_star_kwargs = {}
  args = expected_args[:]

  ## Transform 'defaults' tuple into dict:
  if defaults:
    kw_defaults = dict( zip( args[ -len( defaults ): ], defaults ) )

  else:
    kw_defaults = {}


  ## STEP 1: Apply unnammed args.

  for value in provided_args:

    try:
      ## Populate next argument with next value.
      arg = args.pop( 0 )
      actual_args[ arg ] = value

    except IndexError:

      ## If there is no next argument, can we overflow into *args?
      if star_args:
        actual_star_args.append( value )

      else:

        ## If not: too many arguments were passed to the callable. Abort.
        if len( provided_args ) > 2:
          msg = u"Too many parameters! (Did you forget some quotation marks?)"

        else:
          msg = u"Too many parameters!"

        return False, msg


  ## STEP 2: Apply named args.

  for kwarg, kwvalue in provided_kwargs.iteritems():

    if kwarg in actual_args:

      ## Argument has already been populated! Abort.
      if not isinstance( kwarg, unicode ):
        kwarg = kwarg.decode( "utf-8" )

      return False, u"Parameter %s given several times!" % kwarg

    if kwarg not in expected_args:

      ## Unknown argument. Can we put it into **kwargs?
      if star_kwargs:
        actual_star_kwargs[ kwarg ] = kwvalue

      else:
        ## If not: unknown argument.
        if not isinstance( kwarg, unicode ):
          kwarg = kwarg.decode( "utf-8" )

        return False, u"%s: unknown parameter!" % kwarg

    actual_args[ kwarg ] = kwvalue


  ## STEP 3: Apply default values.

  for default_arg, default_value in kw_defaults.iteritems():

    if default_arg not in actual_args:
      actual_args[ default_arg ] = default_value


  ## STEP 4: Are there still missing arguments?

  if len( expected_args ) > len( actual_args ):

    missing_args = [ arg for arg in expected_args if arg not in actual_args ]
    return False, u"Too few parameters! (Missing parameter '%s')" \
                  % missing_args[ 0 ]


  ## STEP 5: If not, all's good!

  return True, None




def execute( func, args, kwargs ):

  ok, errmsg = match_args_to_function( func, args, kwargs )

  ## TODO: Use match_args_to_function to compute an exact argument -> value
  ## mapping, and call the function with that mapping, so we can be more
  ## flexible about argument order.

  if not ok:
    raise ExecuteError( errmsg )

  return func( *args, **kwargs )
