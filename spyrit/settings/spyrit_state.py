# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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
Declaration of the Spyrit state "settings".
"""

from PySide6.QtCore import QSize
from sunset import Key, Settings

from spyrit import constants
from spyrit.settings.serializers import Size

_default_size = QSize(
    constants.DEFAULT_WINDOW_WIDTH,
    constants.DEFAULT_WINDOW_HEIGHT,
)


def _size_validator(size: QSize) -> bool:
    return size.isValid() and not size.isEmpty()


class SpyritState(Settings):
    window_size = Key(
        _default_size, serializer=Size(), validator=_size_validator
    )
