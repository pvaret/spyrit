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

u"""
:doctest:

>>> from CallbackRegistry import *

"""


import new

from weakref import ref, ReferenceError


class WeakCallableRef:

  u"""\
  Implements a weakref for callables, be they functions or methods.

  Let's create callables of both types:

  >>> def test1():
  ...   pass

  >>> class TestClass:
  ...   def test2( self ):
  ...     pass

  >>> test_obj = TestClass()

  And a little function to tell us when a ref is deleted:

  >>> def call_this_when_ref_deleted( ref ):
  ...   print "Deleted %r!" % ref

  Ok. And now, let's create the weakrefs.

  >>> ref1 = WeakCallableRef( test1, call_this_when_ref_deleted )
  >>> ref2 = WeakCallableRef( test_obj.test2, call_this_when_ref_deleted )

  The original callable can be retrieved by calling the weakref:

  >>> print ref1()  #doctest: +ELLIPSIS
  <function test1 at ...>

  >>> print ref2()  #doctest: +ELLIPSIS
  <bound method TestClass.test2 ...>

  When the original callable is deleted, the notification function is
  triggered.

  >>> del test1  #doctest: +ELLIPSIS
  Deleted <...WeakCallableRef...(test1)...>!

  >>> del test_obj  #doctest: +ELLIPSIS
  Deleted <...WeakCallableRef...(test2)...>!

  And if called, the weakref must now return None:

  >>> print ref1()
  None

  >>> print ref2()
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

      fn  = self._fnref()
      obj = self._objref()

      if None not in ( fn, obj ):
        return new.instancemethod( fn, obj, self._class )

    elif self._fnref:
      return self._fnref()


  def __repr__( self ):

    return "<%s instance at %s (%s)%s>" % (
             self.__class__,
             hex( id( self ) ),
             self._fnname,
             self._dead and "; dead" or ""
           )


  def __del__( self ):

    del self._dead
    del self._objref
    del self._fnref
    del self._class
    del self._callback



class WeakCallable:

  u"""\
  Wraps a callable into a weakly referenced proxy object.

  If the proxy object is called after the reference is deleted, this raises a
  ReferenceError.

  >>> def test1():
  ...   print "Function called!"

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


  def __del__( self ):

    del self._ref


class CallbackRegistry:

  u"""\
  Maintains a registry of weakly referenced callbacks.

  Let's create a registry:

  >>> reg = CallbackRegistry()

  At first, it's empty:

  >>> print len( reg )
  0

  Let's populate it:

  >>> def callback( arg ):
  ...   print "Callback called with argument: %s" % arg

  >>> reg.add( callback )
  >>> print len( reg )
  1

  The registry can trigger the call of all its callbacks with the given
  arguments:

  >>> reg.triggerAll( "Hello world!" )
  Callback called with argument: Hello world!

  And since the callbacks are weakly referenced, they disappear automatically
  from the registry when deleted.

  >>> del callback
  >>> reg.triggerAll( "Hello again!" )  ## nothing happens!
  >>> print len( reg )
  0

  """

  def __init__( self ):

    self.__registry = {}


  def add( self, callback ):

    fnref = WeakCallableRef( callback, self.purgeDeadCallback )
    self.__registry[ id( fnref ) ] = fnref


  def purgeDeadCallback( self, fnref ):

    try:
      del self.__registry[ id( fnref ) ]

    except KeyError:
      pass


  def __len__( self ):

    return len( self.__registry )


  def triggerAll( self, *args, **kwargs ):

    for fnref in self.__registry.itervalues():

      fn = fnref()
      if fn is not None:
        fn( *args, **kwargs )
