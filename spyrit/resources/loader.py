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
Provides utilities to make Spyrit resources available to Qt.
"""

import logging
import os


_resources_loaded = False

# flake8: noqa: F401; ignore possible import error below.
def load() -> bool:
    """
    Attempt to load the compiled Qt resources.

    Returns:
        True if the attempt succeeded, else false.
    """

    global _resources_loaded

    if not _resources_loaded:

        try:
            from . import compiled  # type: ignore

            _resources_loaded = True

        except ImportError:
            this_dir = os.path.dirname(__file__)
            logging.error(
                f"Resources not compiled. In order to compile them, run:\n"
                f" pyside6-rcc --generator python"
                f" --output {this_dir}/resources/compiled.py"
                f" {this_dir}/resources/resources.qrc"
            )

    return _resources_loaded
