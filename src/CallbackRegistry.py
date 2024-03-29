# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

#
# CallbackRegistry.py
#
# Implements the CallbackRegistry class, which provides a simple API to make
# use WeakCallableRef for non-memory-leaking callback storage.
#

"""

:doctest:

>>> from CallbackRegistry import *

"""


from typing import Any, Callable, Sequence

from WeakRef import WeakCallableRef


def safe_call(fn: Callable[..., Any], args: Sequence[Any]) -> Any:
    # This function works like a Qt-like slot, in the sense that it calls the
    # given function with the right number of parameters if more than required
    # are passed.

    while True:
        try:
            return fn(*args)
        except TypeError:
            pass
        if not args:
            break
        # We use the LAST n arguments. The reason for this is, our most common
        # use case for this decorator is to bind configuration changes to the
        # appropriate callbacks. Configuration change notifications emit a (key,
        # value) tuple of arguments, and the typical signatures for our
        # callbacks will use both key and value, or value alone, or nothing at
        # all. If we used the FIRST arguments, then in the second case we'd
        # only transmit the key, which is not as useful as the value.
        args = args[1:]


class CallbackRegistry:

    """
    Maintains a registry of weakly referenced callbacks.

    Let's create a registry:

    >>> reg = CallbackRegistry()

    At first, it's empty:

    >>> print( len( reg ) )
    0

    Let's populate it:

    >>> def callback( arg ):
    ...   print( "Callback called with argument: %s" % arg )

    >>> reg.add( callback )
    >>> print( len( reg ) )
    1

    The registry can trigger the call of all its callbacks with the given
    arguments:

    >>> reg.triggerAll( "Hello world!" )
    Callback called with argument: Hello world!

    And since the callbacks are weakly referenced, they disappear automatically
    from the registry when deleted.

    >>> del callback
    >>> reg.triggerAll( "Hello again!" )  # nothing happens!
    >>> print( len( reg ) )
    0

    """

    def __init__(self):
        self.__registry = {}

    def add(self, callback):
        fnref = WeakCallableRef(callback, self.purgeDeadCallback)
        self.__registry[id(fnref)] = fnref

    def purgeDeadCallback(self, fnref):
        try:
            del self.__registry[id(fnref)]

        except KeyError:
            pass

    def __len__(self):
        return len(self.__registry)

    def triggerAll(self, *args):
        for fnref in self.__registry.values():
            fn = fnref()
            if fn is not None:
                safe_call(fn, args)
