# Copyright (c) 2007-2024 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Implements helpers to manage signal connections.
"""

from typing import Callable, ParamSpec

_P = ParamSpec("_P")


class CallWithArgs:
    """
    Creates a callable that applies the given arguments to the given callable.

    Args:
        callable: The callable to invoke with the given arguments.

        args, kwargs: The arguments to pass to the callable when invoked.
    """

    def __init__(
        self, callable: Callable[_P, None], *args: _P.args, **kwargs: _P.kwargs
    ) -> None:
        self._callable = callable
        self._args = args
        self._kwargs = kwargs

    def __call__(self) -> None:
        """
        Invokes the given callable with the given arguments.
        """

        try:
            self._callable(*self._args, **self._kwargs)
        except RuntimeError:
            # Sadly, it can happen that the callable is a signal whose
            # underlying C++ object was deleted, and there is no way to detect
            # when such is the case. The deletion cannot be handled gracefully
            # through weakref cleverness either, because signals cannot be
            # weakref'ed. So we're left with just catching the exception and
            # discarding it. Sadness.
            pass
