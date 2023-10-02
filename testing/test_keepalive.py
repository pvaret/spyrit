from typing import Any
from pytest_mock import MockerFixture

from PySide6.QtCore import QTimer

from spyrit.network.connection import Connection, Status
from spyrit.network.keepalive import Keepalive
from spyrit.settings.spyrit_settings import KeepaliveMessage, SpyritSettings


class TestKeepalive:
    def test_period_from_settings(self, mocker: MockerFixture) -> None:
        connection = Connection(SpyritSettings.Network())
        timer: Any = mocker.Mock(spec=QTimer)

        settings = SpyritSettings.Network.Keepalive()
        settings.period_secs.set(123)

        Keepalive(connection, settings, timer)

        timer.setInterval.assert_called_once_with(123000)
        timer.setInterval.reset_mock()

        settings.period_secs.set(456)

        timer.setInterval.assert_called_once_with(456000)

    def test_only_start_if_enabled_and_connected(
        self, mocker: MockerFixture
    ) -> None:
        connection = Connection(SpyritSettings.Network())
        timer: Any = mocker.Mock(spec=QTimer)

        settings = SpyritSettings.Network.Keepalive()
        settings.enabled.set(False)

        Keepalive(connection, settings, timer)

        timer.start.assert_not_called()

        settings.enabled.set(True)

        timer.start.assert_not_called()

        settings.enabled.set(False)
        connection.statusChanged.emit(Status.CONNECTED, "")

        timer.start.assert_not_called()

        settings.enabled.set(True)

        timer.start.assert_called_once()

        timer.start.reset_mock()
        timer.stop.reset_mock()

        connection.statusChanged.emit(Status.DISCONNECTED, "")

        timer.start.assert_not_called()
        timer.stop.assert_called_once()

    def test_send_message_on_timer_timeout(self, mocker: MockerFixture) -> None:
        connection = Connection(SpyritSettings.Network())
        connection.send = mocker.Mock(spec=connection.send)
        timer = QTimer()

        settings = SpyritSettings.Network.Keepalive()
        settings.message.set(KeepaliveMessage.CARRIAGE_RETURN)

        Keepalive(connection, settings, timer)

        connection.send.assert_not_called()

        timer.timeout.emit()

        connection.send.assert_called_once_with(
            KeepaliveMessage.CARRIAGE_RETURN.value
        )
