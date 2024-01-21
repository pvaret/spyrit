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

    _TOP_N = 10

    _dump_timer: QTimer
    _obj_counts: dict[str, int]

    def __init__(
        self, parent: QObject, periodicity: int = constants.GC_STATS_DUMP_PERIOD
    ) -> None:
        super().__init__(parent)

        self._obj_counts = {}

        self._dump_timer = QTimer(self)
        self._dump_timer.setInterval(periodicity * 1000)
        self._dump_timer.timeout.connect(self.logGCStats)
        self._dump_timer.start()

    @Slot()
    def logGCStats(self) -> None:
        """
        Computes memory stats and logs them to the debug loglevel.

        Also computes the increase in non-builtin objects between invocations,
        and logs the top to the debug loglevel.
        """

        def _reducer(
            current_tally: tuple[int, int, dict[str, int]],
            obj: object,
        ) -> tuple[int, int, dict[str, int]]:
            count, mem, per_obj_count = current_tally
            obj_name = type(obj).__module__ + "." + type(obj).__qualname__
            per_obj_count.setdefault(obj_name, 0)
            per_obj_count[obj_name] += 1
            return (count + 1, mem + sys.getsizeof(obj), per_obj_count)

        count, mem, per_obj_count = reduce(
            _reducer, gc.get_objects(), (0, 0, {})
        )

        count_string = f"{count:,}"
        mem_string = f"{mem:,}"

        logging.debug(
            "GC stats: %s objects, %s bytes.",
            count_string,
            mem_string,
        )

        _builtins_name = type(True).__module__

        if self._obj_counts:
            obj_count_diff: dict[str, int] = {}

            for obj, count in per_obj_count.items():
                obj_count_diff[obj] = count - self._obj_counts.get(obj, 0)

            diff_counts = sorted(
                [
                    (count, obj)
                    for obj, count in obj_count_diff.items()
                    if obj.split(".")[0] != _builtins_name and count > 0
                ]
            )

            if diff_counts:
                logging.debug("Object count growth:")
                for count, obj in diff_counts[: -(self._TOP_N + 1) : -1]:
                    logging.debug(" - %s: +%s", obj, count)

        self._obj_counts = per_obj_count
