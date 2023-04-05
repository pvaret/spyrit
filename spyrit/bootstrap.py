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
Function to initialize the program and launch it.
"""

import argparse
import logging

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from spyrit import platform, resources
from spyrit.dependency_checker import CHECK_DEPENDENCIES_ARG
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.spyrit_main_ui import SpyritMainUiFactory
from spyrit.ui.spyrit_main_window import SpyritMainWindowFactory
from spyrit.ui.tabbed_ui_factory import TabbedUiFactory


def make_arg_parser(default_config_path: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FOLDER",
        type=str,
        default=default_config_path,
        help="Path to the folder where configuration is stored",
    )
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Enable debugging features",
    )

    # Add this pre-boostrap argument too so that it appears in the help text.

    parser.add_argument(
        CHECK_DEPENDENCIES_ARG,
        action="store_true",
        help="Check for the requisite dependencies and quit",
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
        default_config_path=default_paths.getConfigFolderPath().as_posix()
    )

    # Remove the program name from the arguments, else ArgParse gets
    # confused, then use ArgParse to parse out the Python-side arguments.

    program, remaining_args = args[:1], args[1:]
    flags, remaining_args = parser.parse_known_args(remaining_args)

    default_paths.setConfigFolderPath(flags.config)

    # Put the program name back in with the arguments when creating the
    # QApplication, since Qt expects it.

    app = QApplication(program + remaining_args)

    # Set up logging based on args.

    logging.basicConfig(
        level=logging.DEBUG if flags.debug else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.debug("Debug logging on")

    # Load resources, else bail.

    if not resources.load():
        logging.debug("Resources failed to load")
        return -1

    if QFontDatabase.addApplicationFont(":/fonts/monof55.ttf") == -1:
        logging.debug("Default game font not found in resources")
        return -1

    # Instantiate the settings and autoload/save them.

    settings = SpyritSettings()

    with settings.autosave(default_paths.getConfigFilePath()):
        # Build the UI.

        spyrit_main_window_factory = SpyritMainWindowFactory(settings)
        spyrit_main_ui_factory = SpyritMainUiFactory(settings)

        ui_factory = TabbedUiFactory(
            tabbed_ui_element_factory=spyrit_main_ui_factory,
            tabbed_ui_container_factory=spyrit_main_window_factory,
        )
        ui_factory.createNewUiInNewWindow()

        # And start the show.

        return app.exec()
