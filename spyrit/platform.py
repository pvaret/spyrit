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
Looks up and return platform-specific parameters.
"""

import sys

from spyrit import (
    platform_darwin,
    platform_linux,
    platform_win32,
)
from spyrit.default_paths_base import DefaultPathsBase


def get_default_paths(platform: str = sys.platform) -> DefaultPathsBase:
    match platform:
        case "linux":
            return platform_linux.DefaultPaths()

        case "win32":
            return platform_win32.DefaultPaths()

        case "darwin":
            return platform_darwin.DefaultPaths()

        case _:
            msg = "This program doesn't support your OS. Sorry!"
            raise NotImplementedError(msg)
