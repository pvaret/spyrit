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
Function to initialize the program and launch it.
"""

import argparse
import enum
import logging
import logging.handlers
import sys

from signal import Signals
from types import TracebackType

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from spyrit import constants, platform, resources
from spyrit.default_paths_base import DefaultPathsBase
from spyrit.dependency_checker import CHECK_DEPENDENCIES_ARG
from spyrit.exception_handler import install_exception_handler
from spyrit.gc_stats import GCStats
from spyrit.resources.resources import Font
from spyrit.session.session import Session
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.signal_handlers import save_settings_on_signal
from spyrit.singletonizer import Singletonizer
from spyrit.ui.autocompleter import build_static_word_list_async
from spyrit.ui.styles import StyleManager


class LogTarget(enum.StrEnum):
    """
    Where to send debug logs.
    """

    STDERR = "stderr"
    FILE = "file"
    BOTH = "both"


def _make_arg_parser(default_config_path: str) -> argparse.ArgumentParser:
    """
    Creates a command line argument parser for the application.

    Args:
        default_config_path: The default path where to look for configuration
            files when not otherwise overridden by the user. This is an
            argument because different OSes use a different default path.

    Returns:
        An argument parser, ready to be used.
    """

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
    parser.add_argument(
        "--log-target",
        choices=list(LogTarget),
        default=LogTarget.STDERR,
        action="store",
        help="Where to log debug output: to the terminal's stderr, to the"
        " debug.log file in the configuration folder, or both",
    )
    parser.add_argument(
        "--on-error-abort",
        default=False,
        action="store_true",
        help="Quit the application when an uncaught error occurs",
    )

    # Add this pre-boostrap argument too so that it appears in the help text.

    parser.add_argument(
        CHECK_DEPENDENCIES_ARG,
        action="store_true",
        help="Check for the requisite dependencies and quit",
    )

    return parser


def _build_logger(
    paths: DefaultPathsBase,
    debug: bool = False,
    log_target: LogTarget = LogTarget.STDERR,
) -> logging.Logger:
    """
    Configures and returns the default logger for the application.

    Args:
        paths: The source of truth object for the application's paths.

        debug: Whether to turn on debug logs.

        log_target: Whether to send logs from the standard error, to the
            application's debug log file, or both.

    Returns:
        The default logger, configured.
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")
    if log_target in (LogTarget.STDERR, LogTarget.BOTH):
        logger.addHandler(handler := logging.StreamHandler())
        handler.setFormatter(formatter)
    if log_target in (LogTarget.FILE, LogTarget.BOTH):
        logger.addHandler(
            handler := logging.handlers.TimedRotatingFileHandler(
                filename=paths.getDebugLogFilePath(),
                when="midnight",
                backupCount=10,
            )
        )
        handler.setFormatter(formatter)
    return logger


def _setup_excepthook(logger: logging.Logger) -> None:
    """
    Configures sys.excepthook with a function that just logs the exception to
    the given logger.

    Args:
        logger: The logger on which to log the exception.
    """

    def _log_exception(
        _exc_type_unused: type[BaseException],
        exc_value: BaseException,
        _traceback_unused: TracebackType,
    ) -> None:
        logger.critical("Exception occurred:", exc_info=exc_value)

    sys.excepthook = _log_exception


def _load_resources() -> bool:
    """
    Attempts to load and apply the embedded resources for the application.

    Returns:
        Whether the loading and applying succeeded.
    """

    if not resources.load():
        logging.error("Resources failed to load.")
        return False

    if QFontDatabase.addApplicationFont(Font.NOTO_SANS_MONO_TTF) == -1:
        logging.error("Default game font not found in resources.")
        return False

    return True


def bootstrap(args: list[str]) -> int:
    """
    Initializes and starts the application from the given arguments.

    Args:
        args: The command line arguments for the application. This should
            include the program name as argument 0.

    Returns:
        The application's return code. So, 0 if it ran successfully, some error
        code otherwise.
    """

    # Load default paths.

    default_paths = platform.get_default_paths()

    # Parse Python arguments.

    parser = _make_arg_parser(
        default_config_path=default_paths.getConfigFolderPath().as_posix()
    )

    # Remove the program name from the arguments, else ArgParse gets
    # confused, then use ArgParse to parse out the Python-side arguments.

    program, remaining_args = args[:1], args[1:]
    flags, remaining_args = parser.parse_known_args(remaining_args)
    args = program + remaining_args

    default_paths.setConfigFolderPath(flags.config)

    # Put the program name back in with the arguments when creating the
    # QApplication, since Qt expects it.

    app = QApplication(args)

    # Set up logging based on args.

    logger = _build_logger(default_paths, flags.debug, flags.log_target)
    _setup_excepthook(logger)

    logging.debug("Debug logging on.")

    # Install a custom exception handler.

    install_exception_handler(flags.on_error_abort)

    # Load resources.

    if not _load_resources():
        return -1

    # And start the app.

    return _start_app(app, default_paths, flags.debug)


def _start_app(app: QApplication, paths: DefaultPathsBase, debug: bool) -> int:
    """
    Sets up and starts the given application.

    Args:
        app: The application to be started.

        paths: Path helper object that provides the paths to the application's
            runtime files (settings and such).

        debug: Whether debug mode is on.

    Returns:
        The application's return code. So, 0 if it ran successfully, some error
        code otherwise.
    """

    with Singletonizer(paths.getPidFilePath()) as singletonizer:
        # Ensure there is no other instance of the program running.

        if not singletonizer.isMainInstance():
            remote_pid = singletonizer.notifyNewInstanceStarted()
            logging.info(
                "Another instance of the program is already running with"
                " PID %s. Quitting.",
                remote_pid,
            )
            return 0

        # Instantiate the settings and autoload/save them.

        settings = SpyritSettings()
        state = SpyritState()

        with (
            settings.autosave(
                paths.getConfigFilePath(),
                save_delay=constants.SETTINGS_SAVE_DELAY_MS // 1000,
            ) as settings_saver,
            state.autosave(
                paths.getStateFilePath(),
                save_delay=constants.STATE_SAVE_DELAY_MS // 1000,
            ) as state_saver,
        ):
            # Hook the SIGHUP signal to a helper forcing a save of current
            # settings. Don't assume the signal exists in the enum as it's not
            # true on all OSes.

            if (sighup := getattr(Signals, "SIGHUP", None)) is not None:
                save_settings_on_signal(sighup, settings_saver, state_saver)

            # Build the word completion structure asynchronously.

            build_static_word_list_async()

            # Apply UI style as needed.

            StyleManager(app, settings.ui.style)

            # Build the UI.

            session = Session(settings, state)
            session.newWindow()

            # Open a new window when another instance of the program was
            # launched.

            singletonizer.newInstanceStarted.connect(session.newWindow)

            # Set up the GC stats logger.

            if debug:
                GCStats(app)

            # And start the show.

            return app.exec()
