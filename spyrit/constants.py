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
Provides the product-wide constants. This file should remain a leaf for import
purposes.
"""

# Dependencies

REQUIRED_PYTHON_VERSION: tuple[int, int] = (3, 11)
REQUIRED_QT_VERSION: tuple[int, int] = (6, 2)

# Name

APPLICATION_NAME: str = "SpyritNG"
SPYRIT_VERSION: str = "0.0-dev"

# PID file

PID_FILE_NAME = "spyrit.pid"

# Settings

CONFIG_FILE_NAME_LINUX: str = "spyrit.conf"
CONFIG_FOLDER_NAME_LINUX: str = ".config/spyritng"

CONFIG_FILE_NAME_WINDOWS: str = "Spyrit.ini"
CONFIG_FOLDER_NAME_WINDOWS: str = "SpyritNG"

SETTINGS_SAVE_DELAY_MS: int = 5_000  # milliseconds

# UI

DEFAULT_WINDOW_WIDTH: int = 1000
DEFAULT_WINDOW_HEIGHT: int = 800

ANIMATION_DURATION_MS: int = 500  # milliseconds

# Network

MIN_TCP_PORT = 1
MAX_TCP_PORT = 65535
