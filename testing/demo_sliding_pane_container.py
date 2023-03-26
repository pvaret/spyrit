#!python

import sys
import pathlib

from typing import Optional

from PySide6 import QtCore, QtWidgets

this_file = pathlib.Path(__file__)
this_dir = this_file.parent.absolute()

sys.path.insert(0, str(this_dir.parent))

from spyrit.ui import sliding_pane_container  # noqa: E402


class Pane(QtWidgets.QWidget):
    wantAppend = QtCore.Signal()  # noqa: N815
    wantAppendNoSwitch = QtCore.Signal()  # noqa: N815
    wantPop = QtCore.Signal()  # noqa: N815

    def __init__(
        self, i: int, parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)

        self.setLayout(QtWidgets.QHBoxLayout())

        self._append = QtWidgets.QPushButton(f"Button {i}: Append!")
        self._append.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self._append.clicked.connect(self.wantAppend)
        self.layout().addWidget(self._append)

        self._append_no_switch = QtWidgets.QPushButton(
            f"Button {i}: Append!\n(No switch)"
        )
        self._append_no_switch.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self._append_no_switch.clicked.connect(self.wantAppendNoSwitch)
        self.layout().addWidget(self._append_no_switch)

        self._pop = QtWidgets.QPushButton(f"Button {i}: Pop!")
        self._pop.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self._pop.clicked.connect(self.wantPop)
        self.layout().addWidget(self._pop)


class Container(sliding_pane_container.SlidingPaneContainer):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
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
    app = QtWidgets.QApplication()
    container = Container()
    container.show()
    app.exec()
