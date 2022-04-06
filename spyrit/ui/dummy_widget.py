# TODO: Delete.

import random
import string

from typing import Optional


from PySide6 import QtWidgets

from . import tabbed_ui_element
from spyrit.safe_signal import safe_signal


class DummyWidget(tabbed_ui_element.TabbedUiElement):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        name = "".join(random.choice(string.ascii_uppercase) for _ in range(6))

        self.setWindowTitle(f"window: {name}")
        self.setTabTitle(f"tab: {name}")

        button = QtWidgets.QPushButton("Click!")
        button.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
            )
        )

        safe_signal(button, "clicked").connect(self.wantToDetachToNewWindow)

        self.layout().addWidget(button)


def dummy_widget_factory() -> DummyWidget:

    return DummyWidget()
