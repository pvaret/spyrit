# Copyright (c) 2007-2023 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Various confirmation dialogs.
"""

from typing import Protocol, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget


class _Titled(Protocol):
    """
    A protocol that describes objects that have a human-friendly title.
    """

    def title(self) -> str:
        """
        Returns the human-friendly title for the object.
        """
        ...


def _confirmationDialog(
    widget: QWidget | None,
    title: str,
    message: str,
    confirm_label: str,
    cancel_label: str = "Cancel",
) -> bool:
    """
    Shows a confirmation dialog with the given parameters, and returns the
    user's decision to confirm or not.

    Args:
        widget: The widget whose window to use as the dialog's parent.

        title: The dialog's title.

        message: The dialog's text, formatted as HTML.

        confirm_label: The text of the confirmation button.

        cancel_label: The text of the cancel button.

    Returns:
        True if the user confirmed the action, else False.
    """

    dialog = QMessageBox(widget.window() if widget else None)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle(title)
    dialog.setTextFormat(Qt.TextFormat.RichText)
    dialog.setText(message)

    dialog.addButton(
        confirm := QPushButton(confirm_label),
        QMessageBox.ButtonRole.AcceptRole,
    )
    dialog.addButton(
        cancel := QPushButton(cancel_label),
        QMessageBox.ButtonRole.RejectRole,
    )
    dialog.setDefaultButton(cancel)

    dialog.exec()

    return dialog.clickedButton() is confirm


def askUserIfReadyToClose(
    widget: QWidget | None, instances: Sequence[_Titled]
) -> bool:
    """
    Asks the user to confirm they are really ready to close still connected
    games.

    Args:
        window: The widget to use as the message box's parent.

        instances: The game instances to ask the user about.

    Returns:
        Whether the user accepted to close the connected games.
    """

    title = "Really close?"

    if len(instances) == 1:
        message = (
            f"You are still connected to <b>{instances[0].title()}</b>."
            " Really close?"
        )

    else:
        message = (
            "You are still connected to the following games:<br>"
            + "".join(
                f"<b> • {instance.title()}</b><br>" for instance in instances
            )
            + "<br>"
            + "Really close?"
        )

    return _confirmationDialog(widget, title, message, "Close")


def askUserIfReadyToQuit(
    widget: QWidget | None, instances: Sequence[_Titled]
) -> bool:
    """
    Asks the user to confirm they are really ready to quit the application.

    Args:
        window: The widget to use as the message box's parent.

        instances: The game instances to ask the user about.

    Returns:
        Whether the user accepted to quit.
    """

    title = "Really quit?"

    if len(instances) == 1:
        message = (
            f"You are still connected to <b>{instances[0].title()}</b>."
            " Really quit?"
        )

    else:
        message = (
            "You are still connected to the following games:<br>"
            + "".join(
                f"<b> • {instance.title()}</b><br>" for instance in instances
            )
            + "<br>"
            + "Really quit?"
        )

    return _confirmationDialog(widget, title, message, "Quit")


def askUserIfReadyToDisconnect(
    widget: QWidget | None, instance: _Titled
) -> bool:
    """
    Asks the user to confirm they are really ready to disconnect from the
    current game server.

    Args:
        window: The widget to use as the message box's parent.

        instance: The game instance to ask the user about.

    Returns:
        Whether the user accepted to close the connected games.
    """

    title = "Really disconnect?"
    message = f"You are still connected to <b>{instance.title()}</b>. Really disconnect?"

    return _confirmationDialog(widget, title, message, "Disconnect")
