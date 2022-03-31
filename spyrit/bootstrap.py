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
Function to initialize the program and launch it.
"""

import argparse

from PySide6 import QtWidgets

from . import platform


def make_arg_parser(default_config_path: str) -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        metavar="FOLDER",
        type=str,
        help="Path to the folder where configuration is stored",
        default=default_config_path,
    )
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Enable debugging features",
    )

    return parser


def bootstrap(args: list[str]) -> int:
    "Initializes and starts the application from the given arguments."

    # Create the application object right away, so that Qt can remove its own
    # arguments from the command line.

    app = QtWidgets.QApplication(args)

    # Load default paths.

    default_paths = platform.get_default_paths()

    # Parse remaining arguments.

    parser = make_arg_parser(
        default_config_path=default_paths.getConfigFolderPath()
    )
    flags = parser.parse_args(args[1:])

    default_paths.setConfigFolderPath(flags.config)

    # TODO: Replace with actual application widget.

    mw = QtWidgets.QWidget()
    mw.show()

    # And start the show.

    return app.exec()
