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
Provides the product-wide constants. This file should remain a leaf for import
purposes.
"""

# Dependencies

REQUIRED_PYTHON_VERSION: tuple[int, int] = (3, 11)
REQUIRED_QT_VERSION: tuple[int, int] = (6, 5)

# Name

APPLICATION_NAME: str = "SpyritNG"
SPYRIT_VERSION: str = "0.6-dev"

# Special named files

PID_FILE_NAME: str = "spyrit.pid"
DEBUG_LOG_FILE_NAME: str = "debug.log"

# Settings

CONFIG_FOLDER_NAME_LINUX: str = ".config/spyritng"
CONFIG_FILE_NAME_LINUX: str = "spyrit.conf"
STATE_FILE_NAME_LINUX: str = ".spyrit.state"

CONFIG_FOLDER_NAME_WINDOWS: str = "SpyritNG"
CONFIG_FILE_NAME_WINDOWS: str = "Spyrit.ini"
STATE_FILE_NAME_WINDOWS: str = "Spyrit.state"

SETTINGS_SAVE_DELAY_MS: int = 3_000  # milliseconds
STATE_SAVE_DELAY_MS: int = 10_000  # milliseconds

# UI

DEFAULT_WINDOW_WIDTH: int = 1000
DEFAULT_WINDOW_HEIGHT: int = 800

UI_UNIT_SIZE_PX: int = 16  # pixels
UI_MARGIN_SIZE_PX: int = 2  # pixels
LOGO_WIDTH_UNITS: int = 20  # UI units
FORM_WIDTH_UNITS: int = 20  # UI units

PANE_ANIMATION_DURATION_MS: int = 450  # milliseconds
SCROLL_ANIMATION_DURATION_MS: int = 250  # milliseconds

DEFAULT_FONT_FAMILY: list[str] = ["Noto Sans Mono", "monospace"]
DEFAULT_FONT_POINT_SIZE: int = 12

TAB_TEXT_WIDTH_CHARS: int = 30

OUTPUT_VIEW_WORD_WRAP_COLUMN: int = 100

# Network

UNNAMED_WORLD_NAME: str = "Unnamed world"
EXAMPLE_SERVER: str = "world.example.org"
EXAMPLE_PORT: int = 23
MIN_TCP_PORT: int = 1
MAX_TCP_PORT: int = 65535

# Game data processing

PROCESSOR_BLOCK_SIZE_BYTES: int = 128

# Text processing

VALID_INNER_CHARS: set[str] = set("'-_")

# Internals and debugging

GC_STATS_DUMP_PERIOD: int = 60  # seconds
