#!python

import pathlib
import sys

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit import resources
    from spyrit.settings.spyrit_settings import SpyritSettings
    from spyrit.ui.welcome_pane import WelcomePane

    resources.load()
    app = QApplication()
    pane = WelcomePane(SpyritSettings())
    pane.show()

    app.exec()
