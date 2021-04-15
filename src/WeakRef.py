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
## WeakRef.py
##
## Implements a bunch of weakly referenced objects and containers.
##

"""

:doctest:

>>> from WeakRef import *

"""


import types
import weakref

from typing import Callable, Generic, Optional, TypeVar, Union, cast


## This should normally be constrained to Callable subtypes only. But doing so causes
## the function signature to be lost from the type system when dereferencing the ref.
## TODO: Report bug?
FnType = TypeVar("FnType")


class FunctionRef:
    def __init__(
        self,
        fn: types.FunctionType,
        callback: Callable[[weakref.ReferenceType], None],
    ):
        self._fnref = weakref.ref(fn, callback)

    def ref(self) -> Optional[types.FunctionType]:
        return self._fnref()


class MethodRef:
    def __init__(
        self,
        fn: types.MethodType,
        callback: Callable[[weakref.ReferenceType], None],
    ):
        self._objref = weakref.ref(fn.__self__, callback)
        self._fnref = weakref.ref(fn.__func__, callback)

    def ref(self) -> Optional[types.MethodType]:

        ## Bind the method on the fly, and return it.
        fn = self._fnref()
        obj = self._objref()

        if None in (fn, obj):
            return None

        assert fn is not None  ## Help out the type checker.
        return types.MethodType(fn, obj)


class WeakCallableRef(Generic[FnType]):

    """
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
    <function ...test3 ...>

    When the original callable disappears, the notification function is
    triggered.

    >>> del test1  #doctest: +ELLIPSIS
    Deleted <WeakCallableRef instance at ... (test1); dead>!

    >>> del test_obj  #doctest: +ELLIPSIS
    Deleted <WeakCallableRef instance at ... (test2); dead>!

    >>> import gc
    >>> del TestClass ; _ = gc.collect()  #doctest: +ELLIPSIS
    Deleted <WeakCallableRef instance at ... (test3); dead>!

    And if called, the weakrefs must now return None:

    >>> print( func_ref() )
    None
    >>> print( bound_meth_ref() )
    None
    >>> print( static_meth_ref() )
    None

    """

    def __init__(
        self, fn: FnType, callback: Callable[["WeakCallableRef"], None] = None
    ):

        self._ref: Optional[Union[FunctionRef, MethodRef]]
        self._callback = callback

        if isinstance(fn, types.MethodType):
            self._name = fn.__name__
            self._ref = MethodRef(fn, self.markDead)

        elif isinstance(fn, types.FunctionType):
            self._name = fn.__name__
            self._ref = FunctionRef(fn, self.markDead)

        else:
            raise TypeError("%r must be a function or a method" % fn)

    def markDead(self, unused_objref) -> None:

        if self._ref is not None:

            callback = self._callback

            self._ref = None
            self._callback = None

            if callback:
                callback(self)

    def __call__(self) -> Optional[FnType]:

        if self._ref is not None:
            return cast(FnType, self._ref.ref())

        return None

    def __repr__(self) -> str:

        return "<%s instance at %s (%s)%s>" % (
            self.__class__.__name__,
            hex(id(self)),
            self._name,
            "; dead" if self._ref is None else "",
        )
