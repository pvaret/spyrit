#!python

from collections.abc import Callable, Generator, Iterator
from typing import Any, ClassVar, NoReturn

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)

from spyrit.ui.base_pane import Pane
from spyrit.ui.sliding_pane_container import SlidingPaneContainer


def counter() -> Generator[int, Any, NoReturn]:
    i = 1
    while True:
        yield i
        i += 1


class TestPane(Pane):
    _container: SlidingPaneContainer
    _i: int
    _counter: ClassVar[Iterator[int]] = counter()

    def __init__(self, i: int, parent: SlidingPaneContainer) -> None:
        super().__init__(parent)

        self._i = i
        self._container = container

        self.setLayout(layout := QGridLayout())

        def _make_button(text: str, callback: Callable[[], None]) -> QPushButton:
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
        layout.addWidget(_make_button("Append!", self.appendRight), row, 0, 1, 2)
        row += 1
        layout.addWidget(_make_button("Slide left!", parent.slideLeft), row, 0)
        layout.addWidget(_make_button("Slide right!", parent.slideRight), row, 1)
        row += 1
        button = _make_button("Toggle persistent!", self.togglePersistent)
        layout.addWidget(button, row, 0, 1, 2)
        button.setCheckable(True)

    def appendRight(self) -> None:
        self._container.addPaneRight(TestPane(next(self._counter), self._container))

    @Slot(bool)
    def togglePersistent(self, persistent: bool) -> None:
        self.pane_is_persistent = persistent

    def __del__(self) -> None:
        print(f"Pane {self._i} garbage collected!")


if __name__ == "__main__":
    app = QApplication()
    container = SlidingPaneContainer()
    container.addPaneRight(TestPane(0, container))
    container.show()
    app.exec()
