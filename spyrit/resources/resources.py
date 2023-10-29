# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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
Provides enums that contain the names of the Qt resources that are expected to
exist in the application.
"""

import enum

from typing import Sequence

from spyrit.resources.loader import load

# Ensure the resources are loaded when this file is imported.

load()


class Logo(enum.StrEnum):
    SPYRIT_SVG = ":/logos/spyrit-logo.svg"


class Font(enum.StrEnum):
    NOTO_SANS_MONO_TTF = ":/fonts/NotoSansMono.ttf"


class Icon(enum.StrEnum):
    INPUT_FIELD_SVG = ":/icons/input-field.svg"
    NEW_TAB_SVG = ":/icons/new-tab.svg"
    SEARCH_SVG = ":/icons/search.svg"


Resources: Sequence[type[enum.StrEnum]] = (Logo, Font, Icon)
