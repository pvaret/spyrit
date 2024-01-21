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
Provides utilities to make Spyrit resources available to Qt.
"""

import logging
import pathlib


_resources_loaded: bool = False


def load() -> bool:
    """
    Attempts to load the application's compiled Qt resources.

    Returns:
        True if the attempt succeeded, else False.
    """

    global _resources_loaded

    if not _resources_loaded:
        try:
            # pylint: disable-next=import-outside-toplevel
            import spyrit.resources.___compiled as compiled  # noqa: F401

            _resources_loaded = True
            del compiled

        except ImportError:
            this_file = pathlib.Path(__file__)
            this_dir: str = this_file.parent.absolute().as_posix()

            logging.error(
                "Resources not compiled. In order to compile them, run:\n"
                " pyside6-rcc --generator python"
                " --compress 9 --threshold 0.95"
                " --output %s/___compiled.py"
                " %s/resources.qrc",
                this_dir,
                this_dir,
            )

    return _resources_loaded
