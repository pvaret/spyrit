from PySide6.QtWidgets import QVBoxLayout

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.bars import HBar
from spyrit.ui.buttons import Button
from spyrit.ui.spyrit_logo import SpyritLogo

# TODO: make this a function of the font size.
_UNIT = 16
_WIDTH = 16 * _UNIT


class MainMenuLayout(QVBoxLayout):
    def __init__(self, settings: SpyritSettings) -> None:
        super().__init__()

        self.addWidget(SpyritLogo())

        self.addWidget(HBar())

        self.addSpacing(_UNIT)

        # TODO: Plug button into world creation UI.
        self.addWidget(Button("New world..."))

        # TODO: Add buttons to connect to existing worlds.

        self.addStretch()
