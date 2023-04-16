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
Implements a UI to set up a new world.
"""


from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from spyrit.settings.spyrit_settings import SpyritSettings


class WorldCreationPane(QWidget):
    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel("Creating a new world!"))

        # TODO: Implement.
