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

"""
Provide a workaround to signal type unsafety in PySide6.
"""

from PySide6 import QtCore


def safe_signal(obj: QtCore.QObject, signal_name: str) -> QtCore.SignalInstance:
    """
    Workaround: PySide6 does not declare the signals exported by Qt's classes.
    This wrapper lets us keep the type unsafety contained in a single place. How
    unpleasant, though.
    """

    try:
        signal = getattr(obj, signal_name)
    except AttributeError:
        raise RuntimeError(
            f"Instance of {type(obj)} has no signal named '{signal_name}'"
        )

    if isinstance(signal, QtCore.SignalInstance):
        return signal

    raise RuntimeError(
        f"Attribute '{signal_name}' of {type(obj)} is not a signal"
    )
