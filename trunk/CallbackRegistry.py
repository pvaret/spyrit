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
## CallbackRegistry.py
##
## Registering callbacks for event notification and otherwise is a useful
## practice, but it comes with a serious annoyance: it keeps a reference to
## the callback object beyond the lifespan of that object, causing memory
## leaks if not cautiously coded around.
##
## Normally, you use weak references to solve this kind of issue. But due to
## the implementation details of Python, weak references to bound methods
## are recycled immediately, making them useless as such for this purpose.
##
## Hence the two classes of this file: WeakCallableRef, which implements
## weak references for callables, INCLUDING bound methods, in a way that
## works; and CallbackRegistry, which provides a simple API to make use of
## it for callback storage.
##


import weakref


class WeakCallableRef:
  
  def __init__( s, fn, callback=None ):
  
    assert callable( fn )
  
    s._methname = None
    s._objref   = None
    s._fnref    = None
    s._dead     = False
    s._callback = callback
    
    obj = getattr( fn, "im_self", None )
    
    if obj:  ## fn is a bound method
      s._objref   = weakref.ref( obj, s.markDead )
      s._methname = fn.im_func.func_name

    else:  ## fn is a static method or a plain function
      s._fnref = weakref.ref( fn, s.markDead )
  
  
  def markDead( s, ref ):
    
    s._dead = True
    if s._callback: s._callback( s )
    
    
  def __call__( s ):
    
    if s._dead: return None
    
    if s._objref:  ## bound method
      return getattr( s._objref(), s._methname, None )
      
    else:
      return s._fnref()




class CallbackRegistry:
  
  def __init__( s ):
    
    s.__registry = {}
  
  
  def add( s, callback ):
    
    ref = WeakCallableRef( callback, s.purgeDeadCallback )
    s.__registry[ id( ref ) ] = ref
  
  
  def purgeDeadCallback( s, ref ):
    
    del s.__registry[ id( ref ) ]
  
  
  def triggerAll( s, *args, **kwargs ):
    
    for ref in s.__registry.itervalues():
      fn = ref()
      if fn: fn( *args, **kwargs )
