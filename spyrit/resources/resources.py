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
Provides enums that contain the names of the Qt resources that are expected to
exist in the application.
"""

import enum

from typing import Sequence

from spyrit.resources.loader import load


# Ensure the resources are loaded when this file is imported.

load()


class _Resource(enum.StrEnum):
    """
    This class serves as a marker to identify our resource enums, as opposed to
    generic enums that may not contain valid resource names.
    """


class Logo(_Resource):
    APPLICATION_ICON_SVG = ":/logos/app-icon.svg"
    SPYRIT_SVG = ":/logos/spyrit-logo.svg"


class Font(_Resource):
    NOTO_SANS_MONO_TTF = ":/fonts/NotoSansMono.ttf"


class Icon(_Resource):
    CONNECTION_ON_SVG = ":/icons/connection-on.svg"
    CONNECTION_OFF_SVG = ":/icons/connection-off.svg"
    HOME_SVG = ":/icons/home.svg"
    INPUT_FIELD_SVG = ":/icons/input-field.svg"
    NEW_TAB_SVG = ":/icons/new-tab.svg"
    SEARCH_SVG = ":/icons/search.svg"
    SETTINGS_SVG = ":/icons/settings.svg"
    SWITCH_OFF_SVG = ":/icons/switch-off.svg"
    SWITCH_ON_SVG = ":/icons/switch-on.svg"


class Misc(_Resource):
    WORDLIST_TXT_GZ = ":/misc/wordlist.txt.gz"
    TEST_TXT = ":/misc/test.txt"
    TEST_TXT_GZ = ":/misc/test.txt.gz"


RESOURCES: Sequence[type[_Resource]] = (Logo, Font, Icon, Misc)
