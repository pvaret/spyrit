#!python

import pathlib
import sys


from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

this_file = pathlib.Path(__file__)
this_dir = this_file.parent.absolute()

sys.path.insert(0, this_dir.parent.as_posix())

from spyrit.ui.sliding_pane_container import SlidingPaneContainer  # noqa: E402


class Pane(QWidget):
    wantAppend = Signal()  # noqa: N815
    wantAppendNoSwitch = Signal()  # noqa: N815
    wantPop = Signal()  # noqa: N815

    def __init__(self, i: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setLayout(QHBoxLayout())

        self._append = QPushButton(f"Button {i}: Append!")
        self._append.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._append.clicked.connect(self.wantAppend)
        self.layout().addWidget(self._append)

        self._append_no_switch = QPushButton(
            f"Button {i}: Append!\n(No switch)"
        )
        self._append_no_switch.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._append_no_switch.clicked.connect(self.wantAppendNoSwitch)
        self.layout().addWidget(self._append_no_switch)

        self._pop = QPushButton(f"Button {i}: Pop!")
        self._pop.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._pop.clicked.connect(self.wantPop)
        self.layout().addWidget(self._pop)


class Container(SlidingPaneContainer):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.appendPane(silent=True)

    def appendPane(self, silent: bool = False, switch: bool = True) -> None:
        pane = Pane(self._indexOfLastPane() + 1)
        pane.wantAppend.connect(self.appendPane)
        pane.wantAppendNoSwitch.connect(self.appendPaneNoSwitch)
        pane.wantPop.connect(self.popPane)
        self.append(pane, switch)
        if not silent:
            print("Append!")

    def appendPaneNoSwitch(self) -> None:
        self.appendPane(switch=False)

    def popPane(self) -> None:
        if self._indexOfLastPane() > 0:
            print("Pop!")
        self.pop()


if __name__ == "__main__":
    app = QApplication()
    container = Container()
    container.show()
    app.exec()
