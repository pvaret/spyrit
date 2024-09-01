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
Facilities to process otherwise uncaught exceptions.
"""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false


import logging
import sys

from types import TracebackType
from typing import Callable

import stackprinter


def _make_hook(
    abort_on_error: bool = False,
) -> Callable[[type[BaseException], BaseException, TracebackType | None], None]:
    def hook(
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType | None,
    ) -> None:
        logging.error(
            "Uncaught exception:\n"
            + stackprinter.format((exc_type, exc, tb), reverse=True)
        )

        if abort_on_error:
            logging.error("Uncaught error occurred, quitting...")
            try:
                from PySide6.QtWidgets import QApplication

                app = QApplication.instance()
                if app is not None:
                    app.exit()

            except ImportError:
                pass

            sys.exit(-1)

    return hook


def install_exception_handler(abort_on_error: bool = False) -> None:
    sys.excepthook = _make_hook(abort_on_error)
