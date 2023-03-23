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

import sys
import logging
import pathlib


logger = logging.getLogger(__name__)

_resources_loaded: bool = False


def load() -> bool:
    """
    Attempt to load the compiled Qt resources.

    Returns:
        True if the attempt succeeded, else False.
    """

    global _resources_loaded

    if not _resources_loaded:
        this_file = pathlib.Path(__file__)
        this_dir: str = str(this_file.parent.absolute())
        sys.path.insert(0, this_dir)

        try:
            import ___compiled  # type: ignore  # for when it's missing.

            if ___compiled:
                del ___compiled  # So it's not considered unused.

            _resources_loaded = True

        except ImportError:
            logger.error(
                f"Resources not compiled. In order to compile them, run:\n"
                f" pyside6-rcc --generator python"
                f" --compress 9 --threshold 0.95"
                f" --output {this_dir}/___compiled.py"
                f" {this_dir}/resources.qrc"
            )
        finally:
            sys.path.remove(this_dir)

    return _resources_loaded
