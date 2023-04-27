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

from signal import Signals

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from spyrit import constants, platform, resources
from spyrit.dependency_checker import CHECK_DEPENDENCIES_ARG
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.signal_handlers import save_settings_on_signal
from spyrit.singletonizer import Singletonizer
from spyrit.ui.main_ui_factory import SpyritMainUIFactory
from spyrit.ui.main_window_factory import SpyritMainWindowFactory
from spyrit.ui.tabbed_ui_factory import TabbedUIFactory
from spyrit.ui.theming import ThemeManager


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
        level=logging.DEBUG if flags.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.debug("Debug logging on.")

    # Instantiate the settings and autoload/save them.

    settings = SpyritSettings()
    state = SpyritState()

    with (
        Singletonizer(default_paths.getPidFilePath()) as singletonizer,
        settings.autosave(
            default_paths.getConfigFilePath(),
            save_delay=constants.SETTINGS_SAVE_DELAY_MS // 1000,
        ) as settings_saver,
        state.autosave(
            default_paths.getStateFilePath(),
            save_delay=constants.STATE_SAVE_DELAY_MS // 1000,
        ) as state_saver,
    ):
        # Ensure there is no other instance of the program running.

        if not singletonizer.isMainInstance():
            logging.info(
                "Another instance of the program is already running. Quitting."
            )
            singletonizer.notifyNewInstanceStarted()
            return 0

        # Load resources, else bail.

        if not resources.load():
            logging.error("Resources failed to load.")
            return -1

        if QFontDatabase.addApplicationFont(":/fonts/monof55.ttf") == -1:
            logging.error("Default game font not found in resources.")
            return -1

        # Hook the SIGHUP signal to a helper forcing a save of current settings.
        # Don't assume the signal exists in the enum as it's not true on all
        # OSes.

        if (sighup := getattr(Signals, "SIGHUP", None)) is not None:
            save_settings_on_signal(sighup, settings_saver, state_saver)

        # Apply UI theme as needed.

        ThemeManager(app, settings.ui.theme)

        # Build the UI.

        ui_factory = TabbedUIFactory(
            tabbed_ui_element_factory=SpyritMainUIFactory(settings, state),
            tabbed_ui_container_factory=SpyritMainWindowFactory(
                settings, state
            ),
        )
        ui_factory.createNewUIInNewWindow()

        # Open a new window when another instance of the program was launched.

        singletonizer.newInstanceStarted.connect(
            ui_factory.createNewUIInNewWindow
        )

        # And start the show.

        return app.exec()
