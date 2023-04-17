#!python

import pathlib
import sys

from unittest.mock import Mock

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit import resources
    from spyrit.settings.spyrit_settings import SpyritSettings
    from spyrit.ui.main_ui_remote_protocol import UIRemoteProtocol
    from spyrit.ui.welcome_pane import WelcomePane

    settings = SpyritSettings()
    for name in [
        "Happy world!",
        "Other world!",
        "World with a very long name to see how that works out!",
    ]:
        settings.newSection(name).name.set(name)

    resources.load()
    app = QApplication(sys.argv)
    ui = Mock(spec=UIRemoteProtocol)
    pane = WelcomePane(settings, ui)
    pane.show()

    app.exec()
