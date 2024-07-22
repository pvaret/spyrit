#!python

import pathlib
import sys

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit import resources
    from spyrit.session.instance import SessionInstance
    from spyrit.settings.spyrit_settings import SpyritSettings
    from spyrit.settings.spyrit_state import SpyritState
    from spyrit.ui.welcome_pane import WelcomePane

    settings = SpyritSettings()
    for name in [
        "Happy world!",
        "Other world!",
        "World with a very long name to see how that works out!",
    ]:
        settings.newSection(name).name.set(name)

    state = SpyritState()

    resources.load()
    app = QApplication(sys.argv)
    pane = WelcomePane(settings, SessionInstance())
    pane.show()

    app.exec()
