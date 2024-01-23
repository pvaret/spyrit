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
Implements the UI to configure the server settings of a game.
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import VBar
from spyrit.ui.settings.input_widgets import ServerPortEdit, TextLineEdit
from spyrit.ui.settings.settings_block import SettingsBlock
from spyrit.ui.sizer import Sizer


_WORLD_NAME_HELP = """
**World name** is the name you want to use for this world.
For instance, *Discworld MUD* or *Harper's Tale MOO*.
"""
_SERVER_PORT_HELP = f"""
**Server** and **port** together are the network address that tells programs
like {constants.APPLICATION_NAME} how to connect to this world. For instance:
*discworld.starturtle.net* on port *4242*.

You will normally find them on the world's Web homepage.
"""


class ServerSettingsUI(QWidget):
    """
    Implements a UI to edit server settings.

    Args:
        settings: The settings to be edited with this UI.
    """

    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        sizer = Sizer(self)

        self.setLayout(layout := QHBoxLayout())
        layout.addLayout(settings_layout := QVBoxLayout())
        layout.addWidget(VBar())

        layout.addLayout(help_layout := QVBoxLayout())
        layout.addStretch()
        help_layout.addWidget(help := QLabel())
        help_layout.addStretch()
        help_layout.addStrut(sizer.unitSize() * constants.FORM_WIDTH_UNITS)

        settings_layout.addStrut(sizer.unitSize() * constants.FORM_WIDTH_UNITS)

        help.setTextFormat(Qt.TextFormat.MarkdownText)
        help.setWordWrap(True)

        settings_layout.addWidget(
            block := SettingsBlock(
                TextLineEdit(settings.name), "World name", _WORLD_NAME_HELP
            )
        )
        block.helpTextDisplayRequested.connect(help.setText)
        settings_layout.addSpacing(sizer.unitSize())

        settings_layout.addWidget(
            block := SettingsBlock(
                ServerPortEdit(settings.net.server, settings.net.port),
                help_text=_SERVER_PORT_HELP,
            )
        )
        block.helpTextDisplayRequested.connect(help.setText)

        settings_layout.addStretch()
