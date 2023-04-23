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
Implements a UI to play in a world.
"""


from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLineEdit, QTextEdit, QVBoxLayout

from spyrit import constants
from spyrit.network.connection import Connection
from spyrit.network.processors import (
    ChainProcessor,
    UnicodeProcessor,
    bind_processor_to_connection,
)
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_pane import Pane
from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
from spyrit.ui.scribe import Scribe


class WorldPane(Pane):
    _settings: SpyritSettings
    _ui: UIRemoteProtocol

    def __init__(self, settings: SpyritSettings, ui: UIRemoteProtocol) -> None:
        super().__init__()

        self._settings = settings
        self._ui = ui

        self.active.connect(self._setTitles)

        # WIP test garbage follows.
        # TODO: finish.

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(view := QTextEdit())
        self.layout().addWidget(input := QLineEdit())
        view.setReadOnly(True)
        cursor = view.textCursor()

        connection = Connection(settings.net, parent=self)

        processor = ChainProcessor(
            UnicodeProcessor(settings.net.encoding),
            parent=self,
        )
        bind_processor_to_connection(processor, connection)

        scribe = Scribe(cursor, parent=self)
        processor.fragmentsReady.connect(scribe.inscribe)

        connection.start()

        def on_text_entered() -> None:
            text = input.text()
            if connection.send(text + "\r\n"):
                input.clear()

        input.returnPressed.connect(on_text_entered)

    @Slot()
    def _setTitles(self) -> None:
        world_name = self._settings.name.get() or "Unnamed world"
        self._ui.setTabTitle(world_name)
        self._ui.setWindowTitle(f"{constants.APPLICATION_NAME} - {world_name}")
