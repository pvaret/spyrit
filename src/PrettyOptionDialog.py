# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## PrettyOptionDialog.py
##
## This file holds the PrettyOptionDialog class, which makes use of the
## PrettyOptionPanel widget inside a pretty dialog box.
##


from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QDialogButtonBox

from Separator import Separator


class PrettyOptionDialog(QDialog):
    def __init__(
        self, mapper, panel, header=None, oklabel=None, title=None, parent=None
    ):

        QDialog.__init__(self, parent)

        self.header = header
        self.panel = panel
        self.buttonbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.okbutton = self.buttonbox.button(QDialogButtonBox.Ok)

        if oklabel:
            self.okbutton.setText(oklabel)

        if title:
            self.setWindowTitle(title)

        mapper.settingsValid.connect(self.okbutton.setEnabled)
        mapper.emitSignals()

        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        self.relayout()

    def relayout(self):

        if self.layout():
            return

        self.setLayout(QVBoxLayout(self))

        if self.header:
            self.layout().addWidget(self.header)

        self.layout().addWidget(self.panel)
        self.layout().addWidget(Separator(self))
        self.layout().addWidget(self.buttonbox)
