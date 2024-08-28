#!python

import pathlib
import sys

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit.network.connection import Connection
    from spyrit.settings.spyrit_settings import SpyritSettings
    from spyrit.settings.spyrit_state import SpyritState
    from spyrit.ui.world_pane import make_world_pane

    app = QApplication()

    pane = make_world_pane(
        settings := SpyritSettings(), SpyritState(), Connection(settings.net)
    )
    pane.show()

    app.exec()
