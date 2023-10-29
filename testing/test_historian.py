from PySide6.QtWidgets import QPlainTextEdit

from pytest_mock import MockerFixture

from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.input_history import Historian


class TestHistorian:
    def test_historian(self, mocker: MockerFixture) -> None:
        inputbox = mocker.Mock(spec=QPlainTextEdit)

        state = SpyritState()

        historian = Historian(inputbox, state.history)

        historian.historyNext()

        inputbox.clear.assert_not_called()  # type: ignore
        inputbox.appendPlainText.assert_not_called()  # type: ignore

        historian.historyPrevious()

        inputbox.clear.assert_not_called()  # type: ignore
        inputbox.appendPlainText.assert_not_called()  # type: ignore

        historian.recordNewInput("line 1")
        historian.recordNewInput("line 2")

        inputbox.toPlainText.return_value = ""  # type: ignore
        historian.historyPrevious()

        inputbox.clear.assert_called_once()  # type: ignore
        inputbox.appendPlainText.assert_called_once_with("line 2")  # type: ignore

        inputbox.clear.reset_mock()  # type: ignore
        inputbox.appendPlainText.reset_mock()  # type: ignore

        inputbox.toPlainText.return_value = "line 2"  # type: ignore
        historian.historyPrevious()

        inputbox.clear.assert_called_once()  # type: ignore
        inputbox.appendPlainText.assert_called_once_with("line 1")  # type: ignore

        inputbox.clear.reset_mock()  # type: ignore
        inputbox.appendPlainText.reset_mock()  # type: ignore

        inputbox.toPlainText.return_value = "line 1"  # type: ignore
        historian.historyNext()

        inputbox.clear.assert_called_once()  # type: ignore
        inputbox.appendPlainText.assert_called_once_with("line 2")  # type: ignore

        inputbox.clear.reset_mock()  # type: ignore
        inputbox.appendPlainText.reset_mock()  # type: ignore

        inputbox.toPlainText.return_value = "line 2"  # type: ignore
        historian.historyNext()

        inputbox.clear.assert_called_once()  # type: ignore
        inputbox.appendPlainText.assert_called_once_with("")  # type: ignore

    def test_historian_history_limit(self, mocker: MockerFixture) -> None:
        inputbox = mocker.Mock(spec=QPlainTextEdit)

        state = SpyritState()
        state.history.max_history_length.set(1)

        historian = Historian(inputbox, state.history)
        historian.recordNewInput("line 1")
        historian.recordNewInput("line 2")
        historian.recordNewInput("line 3")

        historian.historyNext()
        inputbox.appendPlainText.assert_not_called()  # type: ignore

        historian.historyPrevious()

        inputbox.appendPlainText.assert_called_once_with("line 3")  # type: ignore
        inputbox.appendPlainText.reset_mock()  # type: ignore

        historian.historyPrevious()

        inputbox.appendPlainText.assert_not_called()  # type: ignore

    def test_historian_saves_state(self, mocker: MockerFixture) -> None:
        inputbox = mocker.Mock(spec=QPlainTextEdit)

        state = SpyritState()

        historian = Historian(inputbox, state.history)

        historian.recordNewInput("1")
        historian.recordNewInput("2")
        historian.recordNewInput("3")

        assert [key.get() for key in state.history.history] == ["1", "2", "3"]

    def test_no_duplicates(self, mocker: MockerFixture) -> None:
        inputbox = mocker.Mock(spec=QPlainTextEdit)

        state = SpyritState()

        historian = Historian(inputbox, state.history)

        historian.recordNewInput("2")
        historian.recordNewInput("1")
        historian.recordNewInput("1")
        historian.recordNewInput("2")

        assert [key.get() for key in state.history.history] == ["2", "1", "2"]
