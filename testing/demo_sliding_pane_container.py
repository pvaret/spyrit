#!python

import pathlib
import sys

from typing import Callable

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


this_file = pathlib.Path(__file__)
this_dir = this_file.parent.absolute()

sys.path.insert(0, this_dir.parent.as_posix())

from spyrit.ui.base_pane import Pane  # noqa: E402
from spyrit.ui.sliding_pane_container import SlidingPaneContainer  # noqa: E402

_counter: int = 0


class TestPane(Pane):
    def __init__(self, i: int) -> None:
        super().__init__()

        self._i = i

        self.setLayout(layout := QGridLayout())

        def _make_button(
            text: str, callback: Callable[[], None]
        ) -> QPushButton:
            button = QPushButton(text)
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
            button.clicked.connect(callback)
            return button

        row = 0
        layout.addWidget(QLabel(f"<b>Pane {i}</b>"), row, 0, 1, 2)
        row += 1
        layout.addWidget(_make_button("Add left!", self.appendLeft), row, 0)
        layout.addWidget(_make_button("Add right!", self.appendRight), row, 1)
        row += 1
        layout.addWidget(_make_button("Slide left!", self.slideLeft), row, 0)
        layout.addWidget(_make_button("Slide right!", self.slideRight), row, 1)
        row += 1
        button = _make_button("Toggle persistent!", self.togglePersistent)
        layout.addWidget(button, row, 0, 1, 2)
        button.setCheckable(True)

    def appendLeft(self) -> None:
        global _counter
        _counter += 1
        self.addPaneLeft(TestPane(_counter))

    def appendRight(self) -> None:
        global _counter
        _counter += 1
        self.addPaneRight(TestPane(_counter))

    @Slot(bool)
    def togglePersistent(self, persistent: bool) -> None:
        self.pane_is_persistent = persistent

    def __del__(self) -> None:
        print(f"Pane {self._i} garbage collected!")


if __name__ == "__main__":
    app = QApplication()
    container = SlidingPaneContainer()
    container.addPaneRight(TestPane(0))
    container.show()
    app.exec()
