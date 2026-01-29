from PySide6.QtWidgets import QPlainTextEdit
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.input_history import Historian


class TestHistorian:
    def test_historian(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        state = SpyritState()

        inputbox = QPlainTextEdit()
        qtbot.addWidget(inputbox)
        clear = mocker.spy(inputbox, "clear")
        append_plain_text = mocker.spy(inputbox, "appendPlainText")
        to_plain_text = mocker.spy(inputbox, "toPlainText")

        historian = Historian(
            inputbox,
            state.history,
            SpyritSettings.KeyShortcuts(),
        )

        historian.historyNext()

        clear.assert_not_called()
        append_plain_text.assert_not_called()

        historian.historyPrevious()

        clear.assert_not_called()
        append_plain_text.assert_not_called()

        historian.recordNewInput("line 1")
        historian.recordNewInput("line 2")

        to_plain_text.return_value = ""
        historian.historyPrevious()

        clear.assert_called_once()
        append_plain_text.assert_called_once_with("line 2")

        clear.reset_mock()
        append_plain_text.reset_mock()

        to_plain_text.return_value = "line 2"
        historian.historyPrevious()

        clear.assert_called_once()
        append_plain_text.assert_called_once_with("line 1")

        clear.reset_mock()
        append_plain_text.reset_mock()

        to_plain_text.return_value = "line 1"
        historian.historyNext()

        clear.assert_called_once()
        append_plain_text.assert_called_once_with("line 2")

        clear.reset_mock()
        append_plain_text.reset_mock()

        to_plain_text.return_value = "line 2"
        historian.historyNext()

        clear.assert_called_once()
        append_plain_text.assert_called_once_with("")

    def test_historian_history_limit(self, mocker: MockerFixture, qtbot: QtBot) -> None:
        state = SpyritState()
        state.history.max_history_length.set(1)

        inputbox = QPlainTextEdit()
        qtbot.addWidget(inputbox)
        append_plain_text = mocker.spy(inputbox, "appendPlainText")

        historian = Historian(inputbox, state.history, SpyritSettings.KeyShortcuts())
        historian.recordNewInput("line 1")
        historian.recordNewInput("line 2")
        historian.recordNewInput("line 3")

        historian.historyNext()
        append_plain_text.assert_not_called()

        historian.historyPrevious()

        append_plain_text.assert_called_once_with("line 3")
        append_plain_text.reset_mock()

        historian.historyPrevious()

        append_plain_text.assert_not_called()

    def test_historian_saves_state(self, qtbot: QtBot) -> None:
        state = SpyritState()

        inputbox = QPlainTextEdit()
        qtbot.addWidget(inputbox)

        historian = Historian(inputbox, state.history, SpyritSettings.KeyShortcuts())

        historian.recordNewInput("1")
        historian.recordNewInput("2")
        historian.recordNewInput("3")

        assert [key.get() for key in state.history.history] == ["1", "2", "3"]

    def test_no_duplicates(self, qtbot: QtBot) -> None:
        state = SpyritState()

        inputbox = QPlainTextEdit()
        qtbot.addWidget(inputbox)
        historian = Historian(inputbox, state.history, SpyritSettings.KeyShortcuts())

        historian.recordNewInput("2")
        historian.recordNewInput("1")
        historian.recordNewInput("1")
        historian.recordNewInput("2")

        assert [key.get() for key in state.history.history] == ["2", "1", "2"]
