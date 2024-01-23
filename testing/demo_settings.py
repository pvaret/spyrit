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
    from spyrit.ui.settings.settings_pane import SettingsPane

    app = QApplication()

    settings = SpyritSettings()
    (test1 := settings.getOrCreateSection("test1")).name.set("Test 1")
    (test2 := settings.getOrCreateSection("test2")).name.set("Test 2")
    (test3 := settings.getOrCreateSection("longname")).name.set(
        "Test 3: Example with a super long name to exhibit the behavior of the UI"
        " in this case"
    )
    (test4 := settings.getOrCreateSection("alsolongname")).name.set(
        "Test 4: AlsoVeryLongButWithoutAnywhereToSplitTheLabelBetweenWordsOhMy"
    )

    pane = SettingsPane(random.choice([settings, test1, test2, test3, test4]))
    pane.show()

    pane.okClicked.connect(pane.close)

    app.exec()
