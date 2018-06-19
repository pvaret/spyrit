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
## WeakRef.py
##
## Implements a bunch of weakly referenced objects and containers.
##

u"""
:doctest:

>>> from WeakRef import *

"""

from __future__ import print_function

import types

from weakref import ref, ReferenceError



class WeakCallableRef( object ):

  u"""
  Implements a weakref for callables, be they functions or methods.

  Due to implementation details, native Python weakrefs on bound methods always
  expire right away. WeakCallableRef, on the other hand, only expires bound
  method references when the object the method is bound to expires. It
  otherwise behaves like native Python weakref for other callables (functions
  and static methods).

  To demonstrate, let's create callables of all three kinds:

  >>> def test1():
  ...   pass

  >>> class TestClass:
  ...   def test2( self ): pass
  ...   @staticmethod
  ...   def test3(): pass

  >>> test_obj = TestClass()

  And a little function to tell us when a ref is deleted:

  >>> def call_on_expire( ref ):
  ...   print( "Deleted %r!" % ref )

  Ok. And now, let's create the weakrefs.

  >>> func_ref        = WeakCallableRef( test1, call_on_expire )
  >>> bound_meth_ref  = WeakCallableRef( test_obj.test2, call_on_expire )
  >>> static_meth_ref = WeakCallableRef( TestClass.test3, call_on_expire )

  The original callable can be retrieved by calling the weakref:

  >>> print( func_ref() )  #doctest: +ELLIPSIS
  <function test1 at ...>

  >>> print( bound_meth_ref() )  #doctest: +ELLIPSIS
  <bound method TestClass.test2 ...>

  >>> print( static_meth_ref() )  #doctest: +ELLIPSIS
  <function test3 ...>

  When the original callable disappears, the notification function is
  triggered.

  >>> del test1  #doctest: +ELLIPSIS
  Deleted <...WeakCallableRef...(test1)...>!

  >>> del test_obj  #doctest: +ELLIPSIS
  Deleted <...WeakCallableRef...(test2)...>!

  >>> del TestClass  #doctest: +ELLIPSIS
  Deleted <...WeakCallableRef...(test3)...>!

  And if called, the weakrefs must now return None:

  >>> print( func_ref() )
  None
  >>> print( bound_meth_ref() )
  None
  >>> print( static_meth_ref() )
  None

  """

  def __init__( self, fn, callback=None ):

    assert callable( fn )

    self._objref   = None
    self._fnref    = None
    self._class    = None
    self._dead     = False
    self._callback = callback
    self._fnname   = ""

    obj = getattr( fn, "im_self", None )

    if obj is not None:  ## fn is a bound method
      self._objref = ref( obj,        self.markDead )
      self._fnref  = ref( fn.im_func, self.markDead )
      self._class  = fn.im_class
      self._fnname = fn.im_func.func_name

    else:  ## fn is a static method or a plain function
      self._fnref  = ref( fn, self.markDead )
      self._fnname = fn.func_name


  def markDead( self, objref ):

    if not self._dead:

      callback = self._callback

      self._dead     = True
      self._objref   = None
      self._fnref    = None
      self._class    = None
      self._callback = None

      if callback:
        return callback( self )


  def __call__( self ):

    if self._objref:  ## bound method

      ## Bind the method on the fly, and return it.
      fn  = self._fnref()
      obj = self._objref()

      if None in ( fn, obj ):
        return None

      return types.MethodType( fn, obj, self._class )

    elif self._fnref:
      return self._fnref()

    else:
      return None


  def __repr__( self ):

    return "<%s instance at %s (%s)%s>" % (
             self.__class__,
             hex( id( self ) ),
             self._fnname,
             self._dead and "; dead" or ""
           )



class WeakCallable:

  u"""\
  Wraps a callable into a weakly referenced proxy object.

  If the proxy object is called after the reference is deleted, this raises a
  ReferenceError.

  >>> def test1():
  ...   print( "Function called!" )

  >>> test_ref = WeakCallable( test1 )
  >>> test_ref()
  Function called!

  >>> del test1
  >>> test_ref()  #doctest: +ELLIPSIS
  Traceback (most recent call last):
  ...
  ReferenceError: Attempted to call dead WeakCallable...

  """

  def __init__( self, fn ):

    self._ref = WeakCallableRef( fn )


  def __call__( self, *args, **kwargs ):

    fn = self._ref()
    if fn is not None:
      return fn( *args, **kwargs )

    raise ReferenceError( "Attempted to call dead WeakCallable %s!" % self )


  def __repr__( self ):

    return "<%s instance at %s%s>" % (
             self.__class__,
             hex( id( self ) ),
             ( self._ref() is None ) and "; dead" or ""
           )
