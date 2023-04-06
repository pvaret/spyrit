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
Helpers to perform specific operations in response to certain signals.
"""

import logging
import signal

from types import FrameType
from typing import Optional

from sunset import AutoSaver


def save_settings_on_signal(
    sig: int | signal.Signals, *savers: AutoSaver
) -> None:
    """
    Attaches a signal handler for the given signal that forces the given
    AutoSavers to save.

    Args:
        sig: The signal for which to attach the handler.

        savers: The AutoSaver on which to trigger a save.
    """

    default_handler = signal.getsignal(sig)

    def _on_signal(
        sig: int | signal.Signals, frame: Optional[FrameType]
    ) -> None:
        logging.info("Signal received -- saving settings.")

        for saver in savers:
            logging.debug(f"Saving {saver.path()}...")
            saver.doSave()

        if (
            default_handler is not None
            and not isinstance(default_handler, int)
            and not isinstance(default_handler, signal.Handlers)
        ):
            default_handler(sig, frame)

    try:
        signal.signal(sig, _on_signal)
    except ValueError as e:
        logging.warning(f"Failed to install signal handler: {e}")
