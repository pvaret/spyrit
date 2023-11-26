#!python

import pathlib
import random
import sys

from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit.settings.spyrit_settings import SpyritSettings
    from spyrit.ui.settings_pane import SettingsPane

    app = QApplication()

    settings = SpyritSettings()
    (test1 := settings.getOrCreateSection("Test 1")).name.set("Test 1")
    (test2 := settings.getOrCreateSection("Test 2")).name.set("Test 2")
    pane = SettingsPane(random.choice([settings, test1, test2]))
    pane.show()

    app.exec()
