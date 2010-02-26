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
## ConfigObserver.py
##
## This file holds ConfigObserver, a helper class that monitors changes in a
## Configuration object and calls the appropriate callback when that happens.
##

import inspect
import weakref

from functools        import wraps
from CallbackRegistry import CallbackRegistry


SLOTIFIED_FN_CACHE = weakref.WeakKeyDictionary()

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

    args = args[ :n_args ]

    return fn( *args )

  ## Keep a reference to the slotified version:
  SLOTIFIED_FN_CACHE[ fn ] = slotified

  return slotified



class ConfigObserver:

  def __init__( s, conf ):

    s.callbacks = {}

    conf.registerNotifier( s.notify )


  def notify( s, key, value ):

    callbacks = s.callbacks.get( key, None )

    if callbacks:
      callbacks.triggerAll( key, value )


  def addCallback( s, keys, callback ):

    if type( keys ) not in ( type( [] ), type( () ) ): keys = [ keys ]

    callback = slotify( callback )

    for key in keys:
      s.callbacks.setdefault( key, CallbackRegistry() ).add( callback )

    return s  ## Return self, so as to make it possible to chain calls.


  def __del__( s ):

    s.callbacks = None
