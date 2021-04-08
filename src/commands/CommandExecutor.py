# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
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

"""

:doctest:

>>> from commands.CommandExecutor import *

"""


import inspect


class ExecuteError(RuntimeError):
    pass


def match_args_to_function(callable, provided_args, provided_kwargs):

    """
    Check that the given arguments fit the given callable's spec.

    Given a few simple functions:

    >>> def simple( a, b=None ):
    ...   pass
    >>> def simple_args( a, b=None, *args ):
    ...   pass
    >>> def simple_kwargs( a, b=None, **kwargs ):
    ...   pass

    Let us see how it works:

    >>> ok, msg = match_args_to_function( simple, ( "a", "b" ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )
    True : None

    >>> ok, msg = match_args_to_function( simple, ( "a", ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )
    True : None

    >>> ok, msg = match_args_to_function( simple, (), {} )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Missing argument a!
    False : Too few parameters! (Missing parameter 'a')

    >>> ok, msg = match_args_to_function( simple, (), { "a": 1 } )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Passing kwargs also works.
    True : None

    >>> ok, msg = match_args_to_function( simple, ( "a" ), { "c": 1 } )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Passing an unexpected argument
    ...                                   ## doesn't, though.
    False : c: unknown parameter!

    >>> ok, msg = match_args_to_function( simple, ( "a" ), { "a": 1 } )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Neither does passing a redundant
    ...                                   ## argument.
    False : Parameter 'a' passed several times!

    >>> ok, msg = match_args_to_function( simple, ( "a", "b", "c" ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )  ## And neither does passing too many
    ...                                   ## arguments.
    False : Too many parameters! (Did you forget some quotation marks?)

    >>> ok, msg = match_args_to_function( simple_args, ( "a", "b", "c" ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Unless the function accepts *args.
    True : None

    >>> ok, msg = match_args_to_function(
    ...     simple_kwargs, ( "a", "b" ), { "c": 1 } )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Or the function accepts **kwargs.
    True : None

    Class method calls also work:

    >>> class A( object ):
    ...   def method( self, a ):
    ...     pass
    ...   @classmethod
    ...   def classmethod( cls, a ):
    ...     pass
    ...   @staticmethod
    ...   def staticmethod( a ):
    ...     pass

    First, note that this does not work on class instanciations:

    >>> match_args_to_function( A, (), {} )
    Traceback (most recent call last):
      ...
    TypeError: Tried to call match_args_to_function on a class!

    >>> a = A()

    >>> ok, msg = match_args_to_function( a.method, ( "a" ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )  ## Instance methods work like you'd
    ...                                   ## expect.
    True : None

    >>> ok, msg = match_args_to_function( a.classmethod, ( "a" ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )  ## But so do class methods.
    True : None

    >>> ok, msg = match_args_to_function( a.staticmethod, ( "a" ), {} )
    >>> print( "%s : %s" % ( ok, msg ) )  ## And static methods.
    True : None

    """

    if inspect.isclass(callable):
        raise TypeError("Tried to call match_args_to_function on a class!")

    ## TODO: replace with inspect.signature in Python 3.
    try:
        call_args = inspect.getargspec(callable)
        expected_args, star_args, star_kwargs, defaults = call_args
    except TypeError:
        raise TypeError(
            "Tried to call match_args_to_function on a non-Python " "function!"
        )

    ## Reminder:
    ##   - expected_args is the list of the callable's arguments.
    ##   - defaults is a tuple of default arguments.
    ##   - star_args and star_kwargs are the names of the * and ** arguments
    ##     (usually 'args' and 'kwargs').

    ## Account for implicit 'self' argument in methods:
    if inspect.ismethod(callable):
        expected_args.pop(0)

    actual_args = {}
    actual_star_args = []
    actual_star_kwargs = {}
    args = expected_args[:]

    ## Transform 'defaults' tuple into dict:
    if defaults:
        kw_defaults = dict(zip(args[-len(defaults) :], defaults))

    else:
        kw_defaults = {}

    ## STEP 1: Apply unnammed args.

    for value in provided_args:

        try:
            ## Populate next argument with next value.
            arg = args.pop(0)
            actual_args[arg] = value

        except IndexError:

            ## If there is no next argument, can we overflow into *args?
            if star_args:
                actual_star_args.append(value)

            else:

                ## If not: too many arguments were passed to the callable. Abort.
                if len(provided_args) > 2:
                    msg = "Too many parameters! (Did you forget some quotation marks?)"

                else:
                    msg = "Too many parameters!"

                return False, msg

    ## STEP 2: Apply named args.

    for kwarg, kwvalue in provided_kwargs.items():

        if kwarg in actual_args:

            ## Argument has already been populated! Abort.
            if not isinstance(kwarg, type("")):
                kwarg = kwarg.decode("utf-8")

            return False, "Parameter '%s' passed several times!" % kwarg

        if kwarg not in expected_args:

            ## Unknown argument. Can we put it into **kwargs?
            if star_kwargs:
                actual_star_kwargs[kwarg] = kwvalue

            else:
                ## If not: unknown argument.
                if not isinstance(kwarg, type("")):
                    kwarg = kwarg.decode("utf-8")

                return False, "%s: unknown parameter!" % kwarg

        actual_args[kwarg] = kwvalue

    ## STEP 3: Apply default values.

    for default_arg, default_value in kw_defaults.items():

        if default_arg not in actual_args:
            actual_args[default_arg] = default_value

    ## STEP 4: Are there still missing arguments?

    if len(expected_args) > len(actual_args):

        missing_args = [arg for arg in expected_args if arg not in actual_args]
        return False, (
            "Too few parameters! (Missing parameter '%s')" % missing_args[0]
        )

    ## STEP 5: If not, all's good!

    return True, None


def execute(func, args, kwargs):

    ok, errmsg = match_args_to_function(func, args, kwargs)

    ## TODO: Use match_args_to_function to compute an exact argument -> value
    ## mapping, and call the function with that mapping, so we can be more
    ## flexible about argument order.

    if not ok:
        raise ExecuteError(errmsg)

    return func(*args, **kwargs)
