#!python

import pathlib
import sys

from PySide6.QtWidgets import QApplication, QLabel


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit.ui.base_dialog_pane import BaseDialogPane

    app = QApplication()

    text = QLabel("This is a dialog!")
    pane = BaseDialogPane(text)
    pane.okClicked.connect(lambda: print("OK clicked!"))
    pane.cancelClicked.connect(lambda: print("Cancel clicked!"))
    pane.show()

    app.exec()
