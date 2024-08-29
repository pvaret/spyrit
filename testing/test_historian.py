import unittest.mock

from typing import Iterator

import pytest

from pytest_mock import MockerFixture

from PySide6.QtWidgets import QApplication, QPlainTextEdit

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.input_history import Historian


@pytest.fixture
def inputbox(mocker: MockerFixture) -> Iterator[QPlainTextEdit]:
    """
    Provides a QPlainTextEdit with suitably mocked methods.

    Also creates a QApplication for the duration of the test... else
    instantiating QPlainTextEdit fails hard.
    """
    app = QApplication()

    inputbox = QPlainTextEdit()
    inputbox.clear = mocker.stub()
    inputbox.appendPlainText = mocker.stub()
    inputbox.toPlainText = mocker.stub()
    yield inputbox

    app.shutdown()


class TestHistorian:
    def test_historian(self, inputbox: unittest.mock.Mock) -> None:

        state = SpyritState()

        historian = Historian(
            inputbox,
            state.history,
            SpyritSettings.KeyShortcuts(),
        )

        historian.historyNext()

        inputbox.clear.assert_not_called()
        inputbox.appendPlainText.assert_not_called()

        historian.historyPrevious()

        inputbox.clear.assert_not_called()
        inputbox.appendPlainText.assert_not_called()

        historian.recordNewInput("line 1")
        historian.recordNewInput("line 2")

        inputbox.toPlainText.return_value = ""
        historian.historyPrevious()

        inputbox.clear.assert_called_once()
        inputbox.appendPlainText.assert_called_once_with("line 2")

        inputbox.clear.reset_mock()
        inputbox.appendPlainText.reset_mock()

        inputbox.toPlainText.return_value = "line 2"
        historian.historyPrevious()

        inputbox.clear.assert_called_once()
        inputbox.appendPlainText.assert_called_once_with("line 1")

        inputbox.clear.reset_mock()
        inputbox.appendPlainText.reset_mock()

        inputbox.toPlainText.return_value = "line 1"
        historian.historyNext()

        inputbox.clear.assert_called_once()
        inputbox.appendPlainText.assert_called_once_with("line 2")

        inputbox.clear.reset_mock()
        inputbox.appendPlainText.reset_mock()

        inputbox.toPlainText.return_value = "line 2"
        historian.historyNext()

        inputbox.clear.assert_called_once()
        inputbox.appendPlainText.assert_called_once_with("")

    def test_historian_history_limit(
        self, inputbox: unittest.mock.Mock
    ) -> None:
        state = SpyritState()
        state.history.max_history_length.set(1)

        historian = Historian(
            inputbox, state.history, SpyritSettings.KeyShortcuts()
        )
        historian.recordNewInput("line 1")
        historian.recordNewInput("line 2")
        historian.recordNewInput("line 3")

        historian.historyNext()
        inputbox.appendPlainText.assert_not_called()

        historian.historyPrevious()

        inputbox.appendPlainText.assert_called_once_with("line 3")
        inputbox.appendPlainText.reset_mock()

        historian.historyPrevious()

        inputbox.appendPlainText.assert_not_called()

    def test_historian_saves_state(self, inputbox: unittest.mock.Mock) -> None:
        state = SpyritState()

        historian = Historian(
            inputbox, state.history, SpyritSettings.KeyShortcuts()
        )

        historian.recordNewInput("1")
        historian.recordNewInput("2")
        historian.recordNewInput("3")

        assert [key.get() for key in state.history.history] == ["1", "2", "3"]

    def test_no_duplicates(self, inputbox: unittest.mock.Mock) -> None:
        state = SpyritState()

        historian = Historian(
            inputbox, state.history, SpyritSettings.KeyShortcuts()
        )

        historian.recordNewInput("2")
        historian.recordNewInput("1")
        historian.recordNewInput("1")
        historian.recordNewInput("2")

        assert [key.get() for key in state.history.history] == ["2", "1", "2"]
