#!python

import pathlib
import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class TestButton(QPushButton):
    def __init__(self, label: str) -> None:
        super().__init__(label)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit.ui.bars import HBar, VBar

    app = QApplication()

    w = QWidget()
    hlayout = QHBoxLayout()
    w.setLayout(hlayout)
    hlayout.addWidget(TestButton("Button 1"))
    hlayout.addWidget(VBar())
    vlayout = QVBoxLayout()
    hlayout.addLayout(vlayout)
    vlayout.addWidget(TestButton("Button 2"))
    vlayout.addWidget(HBar())
    vlayout.addWidget(TestButton("Button 3"))
    w.show()

    app.exec()
