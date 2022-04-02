# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

#
# ConfirmDialog.py
#
# Provides a simpler confirmation dialog wrapper function.
#


from PyQt6.QtWidgets import QMessageBox


def confirmDialog(title, msg, okbutton, widget=None):

    messagebox = QMessageBox(widget)

    messagebox.setIcon(QMessageBox.Icon.Question)
    messagebox.setWindowTitle(title)
    messagebox.setText(msg)

    messagebox.addButton(okbutton, QMessageBox.ButtonRole.AcceptRole)
    messagebox.addButton(QMessageBox.StandardButton.Cancel)

    return messagebox.exec() != QMessageBox.StandardButton.Cancel
