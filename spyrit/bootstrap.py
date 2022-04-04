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
from .ui import dummy_widget, tabbed_ui_factory


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
    """
    Initializes and starts the application from the given arguments.
    """

    # Load default paths.

    default_paths = platform.get_default_paths()

    # Parse Python arguments.

    parser = make_arg_parser(
        default_config_path=default_paths.getConfigFolderPath()
    )

    # Remove the program name from the arguments, else ArgParse gets
    # confused, then use ArgParse to parse out the Python-side arguments.

    program, remaining_args = args[:1], args[1:]
    flags, remaining_args = parser.parse_known_args(remaining_args)

    default_paths.setConfigFolderPath(flags.config)

    # Put the program name back in with the arguments when creating the
    # QApplication, since Qt expects it.

    app = QtWidgets.QApplication(program + remaining_args)

    # TODO: Replace with actual application widget.

    mw_factory = tabbed_ui_factory.TabbedUiFactory(
        tabbed_ui_element_factory=dummy_widget.dummy_widget_factory
    )
    mw_factory.createNewUiInNewWindow()

    # And start the show.

    return app.exec()
