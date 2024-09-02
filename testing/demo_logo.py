#!python

import pathlib
import sys

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit import constants
    from spyrit import resources
    from spyrit.ui.spyrit_logo import SpyritLogo

    resources.load()
    app = QApplication()
    logo = SpyritLogo(constants.LOGO_WIDTH_UNITS * constants.UI_UNIT_SIZE_PX)
    logo.show()
    app.exec()
