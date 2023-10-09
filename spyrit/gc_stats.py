# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
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
Holds a class that periodically computes and logs garbage collection and memory
usage stats.
"""

import gc
import logging
import sys

from functools import reduce

from PySide6.QtCore import QObject, QTimer, Slot

from spyrit import constants


class GCStats(QObject):
    """
    Periodically collects and logs memory usage statistics at the debug
    loglevel.

    Args:
        parent: What object to parent this one to. Used for lifetime
            management. Typically this will be the QApplication instance.

        periodicity: How frequently, in seconds, to compute and log the stats.
    """

    _dump_timer: QTimer

    def __init__(
        self, parent: QObject, periodicity: int = constants.GC_STATS_DUMP_PERIOD
    ) -> None:
        super().__init__(parent)

        self._dump_timer = QTimer(self)
        self._dump_timer.setInterval(periodicity * 1000)
        self._dump_timer.timeout.connect(self.logGCStats)
        self._dump_timer.start()

    @Slot()
    def logGCStats(self) -> None:
        """
        Computes memory stats and logs them to the debug loglevel.
        """

        def _reducer(
            current_tally: tuple[int, int],
            obj: object,
        ) -> tuple[int, int]:
            count, mem = current_tally
            return (count + 1, mem + sys.getsizeof(obj))

        count, mem = reduce(_reducer, gc.get_objects(), (0, 0))

        count_string = f"{count:,}"
        mem_string = f"{mem:,}"

        logging.debug(
            "GC stats: %s objects, %s bytes.",
            count_string,
            mem_string,
        )
