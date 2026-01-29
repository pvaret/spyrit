# Copyright (c) 2007-2025 Pascal Varet <p.varet@gmail.com>
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
Provides utilities to make Spyrit resources available to Qt.
"""

import importlib
import logging

from PySide6.QtCore import QFile

from spyrit.resources.resources import RESOURCES


def load() -> bool:
    """
    Attempts to load the application's compiled Qt resources.

    Returns:
        True if the attempt succeeded, else False.
    """

    try:
        importlib.import_module("spyrit.__resources__")

    except ImportError:  # pragma: no cover
        logging.error(  # noqa: TRY400  # Actually don't print the exception.
            "Resources not compiled. In order to compile them, run:\n"
            "  hatch build --ext"
        )
        return False

    return all(
        QFile.exists(filename)
        for resource_type in RESOURCES
        for filename in resource_type
    )
