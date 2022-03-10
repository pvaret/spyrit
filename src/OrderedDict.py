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
## OrderedDict.py
##
## A dict-like class that remembers the order of its keys.
##

"""
:doctest:

>>> from OrderedDict import *

"""


from typing import Any, Iterable


class OrderedDict:
    """
    A dict class the remembers the insertion order of its elements.

    >>> d = OrderedDict()
    >>> d["a"] = 1
    >>> d["b"] = 2
    >>> d["c"] = 3
    >>> d["d"] = 4
    >>> print(d)
    {'a':1, 'b':2, 'c':3, 'd':4}

    """

    def __init__(self, init: Iterable[tuple[Any, Any]] = ()):

        self.__dict = {}
        self.__ordered_keys = []

        for k, v in init:
            self[k] = v

    def __repr__(self):
        return (
            "{"
            + ", ".join(("%s:%s" % (repr(k), repr(v)) for k, v in self.items()))
            + "}"
        )

    def __setitem__(self, key, value):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> d["e"] = 5
        >>> print(d)
        {'a':1, 'b':2, 'c':3, 'd':4, 'e':5}

        >>> d["c"] = 5
        >>> print(d)
        {'a':1, 'b':2, 'c':5, 'd':4, 'e':5}

        """

        # Setting an already existing key does not change its position.
        if key not in self.__dict:
            self.__ordered_keys.append(key)

        self.__dict[key] = value

    def __getitem__(self, key):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> d["b"]
        2
        >>> d["e"]  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: ...

        """

        if key not in self.__dict:
            raise KeyError(key)

        return self.__dict[key]

    def __delitem__(self, key):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> del d["c"]
        >>> print(d)
        {'a':1, 'b':2, 'd':4}

        >>> del d[ "c" ]  #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: ...

        """

        if key not in self.__dict:
            raise KeyError(key)

        del self.__dict[key]
        self.__ordered_keys.remove(key)

    def __contains__(self, key):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> "a" in d
        True
        >>> "e" in d
        False

        """

        return key in self.__dict

    def __iter__(self):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> for k in iter(d):
        ...   print(k)
        a
        b
        c
        d

        """

        return iter(self.__ordered_keys)

    def values(self):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> for v in d.values():
        ...   print(v)
        1
        2
        3
        4

        """

        return (self.__dict[k] for k in self.__ordered_keys)

    def setdefault(self, key, defaultvalue):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> print(d.setdefault("a", 5 ))
        1
        >>> print(d.setdefault("e", 6))
        6
        >>> print(d)
        {'a':1, 'b':2, 'c':3, 'd':4, 'e':6}

        """

        if key not in self:
            self[key] = defaultvalue

        return self[key]

    def items(self):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> for k, v in d.items():
        ...   print((k, v))
        ('a', 1)
        ('b', 2)
        ('c', 3)
        ('d', 4)

        """

        return ((k, self.__dict[k]) for k in self.__ordered_keys)

    def insert(self, index, key, value):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> d.insert(2, "e", 5)
        >>> print(d)
        {'a':1, 'b':2, 'e':5, 'c':3, 'd':4}

        """

        if key in self.__dict:
            del self[key]

        self.__dict[key] = value
        self.__ordered_keys.insert(index, key)

    def lastvalue(self):
        """
        >>> d = OrderedDict((("a", 1), ("b", 2), ("c", 3), ("d", 4)))
        >>> print(d.lastvalue())
        4

        >>> d = OrderedDict()
        >>> print(d.lastvalue())
        None

        """

        if not self.__ordered_keys:
            return None

        return self.__dict[self.__ordered_keys[-1]]
