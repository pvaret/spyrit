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
Looks up and return platform-specific parameters.
"""

import sys

from spyrit import (
    default_paths_base,
    platform_darwin,
    platform_linux,
    platform_win32,
)


def get_default_paths() -> default_paths_base.DefaultPathsBase:
    if sys.platform == "linux":
        return platform_linux.DefaultPaths()

    if sys.platform == "win32":
        return platform_win32.DefaultPaths()

    if sys.platform == "darwin":
        return platform_darwin.DefaultPaths()

    raise NotImplementedError("This program doesn't support your OS. Sorry!")
