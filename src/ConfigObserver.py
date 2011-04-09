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
## ConfigObserver.py
##
## This file holds ConfigObserver, a helper class that monitors changes in a
## Configuration object and calls the appropriate callback when that happens.
##

import inspect

from functools        import wraps
from CallbackRegistry import CallbackRegistry, WeakCallableRef



class SlotifiedFunctionReferenceCache:
  """Keep a reference to slotified functions so they're not garbage collected
  right away.

  """

  def __init__( self ):

    self.cache = {}


  def __setitem__( self, func, slotified_func ):

    fnref = WeakCallableRef( func, self.expire )
    self.cache[ id( fnref ) ] = ( func, slotified_func )


  def expire( self, fnref ):

    del self.cache[ id( fnref ) ]


SLOTIFIED_FN_CACHE = SlotifiedFunctionReferenceCache()




def slotify( fn ):

  ## This decorator turns a function or method into a Qt-like slot, in the
  ## sense that it gets called with the right number of parameters if more
  ## than required are passed.

  @wraps( fn )
  def slotified( *args ):

    ( fn_args, varargs, varkw, defaults ) = inspect.getargspec( fn )

    if varargs:
      return fn( *args )

    n_args = len( fn_args )

    if inspect.ismethod( fn ):
      ## Account for 'self' implicit argument.
      n_args -= 1

    if not n_args:
      return fn()

    ## We use the LAST n arguments. The reason for this is, our most common
    ## use case for this decorator is to bind configuration changes to
    ## the appropriate callbacks. Configuration change notifications emit
    ## a (key, value) tuple of arguments, and the typical signatures for our
    ## callbacks will use both key and value, or value alone, or nothing at
    ## all.
    ## If we used the FIRST n arguments, then in the second case we'd only
    ## transmit the key, which is not as useful as the value.

    args = args[ -n_args: ]

    return fn( *args )

  ## Keep a reference to the slotified version:
  SLOTIFIED_FN_CACHE[ fn ] = slotified

  return slotified



class ConfigObserver:

  def __init__( self, conf ):

    self.callbacks = {}

    conf.registerNotifier( self.notify )


  def notify( self, key, value ):

    callbacks = self.callbacks.get( key, None )

    if callbacks:
      callbacks.triggerAll( key, value )


  def addCallback( self, keys, callback ):

    if type( keys ) not in ( type( [] ), type( () ) ): keys = [ keys ]

    callback = slotify( callback )

    for key in keys:
      self.callbacks.setdefault( key, CallbackRegistry() ).add( callback )

    return self  ## Return self, so as to make it possible to chain calls.


  def __del__( self ):

    self.callbacks = None
