#!python


from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from spyrit.settings.scrambled_text import ScrambledText


class ScrambleUI(QWidget):

    _input: QLineEdit
    _output: QLineEdit

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._input = QLineEdit()
        self._output = QLineEdit("Nothing yet.")

        self.setLayout(layout := QGridLayout())
        layout.addWidget(QLabel("Password"), 0, 0)
        layout.addWidget(self._input, 0, 1)
        layout.addWidget(scramble := QPushButton("Scramble!"), 0, 2)
        layout.addWidget(QLabel("Scrambled"))
        layout.addWidget(self._output, 1, 1)

        self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._output.setReadOnly(True)

        scramble.clicked.connect(self._scramble)

    @Slot()
    def _scramble(self) -> None:
        text = self._input.text()
        scramble = ScrambledText(text)
        self._output.setText(scramble.toStr())


if __name__ == "__main__":
    app = QApplication()
    widget = ScrambleUI()
    widget.show()
    app.exec()
