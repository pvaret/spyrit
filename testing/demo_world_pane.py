#!python

import pathlib
import sys

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    this_file = pathlib.Path(__file__)
    this_dir = this_file.parent.absolute()

    sys.path.insert(0, this_dir.parent.as_posix())

    from spyrit.network.connection import Connection, ConnectionStatus, Status
    from spyrit.settings.spyrit_settings import Encoding, SpyritSettings
    from spyrit.settings.spyrit_state import SpyritState
    from spyrit.ui.world_pane import make_processor, make_world_pane

    app = QApplication()

    settings = SpyritSettings()
    settings.net.server.set("localhost")
    settings.net.port.set(4201)
    settings.net.encoding.set(Encoding.UTF8)

    connection = Connection(settings.net)

    pane = make_world_pane(
        settings,
        SpyritState(),
        ConnectionStatus(connection),
        processor := make_processor(connection, settings),
    )

    def fake_start() -> None:
        connection.statusChanged.emit(Status.CONNECTED, "")

    def fake_stop() -> None:
        connection.statusChanged.emit(Status.DISCONNECTED, "")

    def echo(text: str) -> None:
        connection.dataReceived.emit(
            f"Received: {text}".encode(settings.net.encoding.get())
        )

    pane.startConnection.connect(fake_start)
    pane.stopConnection.connect(fake_stop)
    pane.sendUserInput.connect(echo)
    pane.closePaneRequested.connect(pane.close)

    pane.show()

    app.exec()
