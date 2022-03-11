# Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
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
# SettingsPanel.py
#
# This helper class take care of the boilerplate in the creation of a simple
# settings form.
#


from PyQt5.QtWidgets import QWidget, QFormLayout


class SettingsPanel(QWidget):

    MARGINS = (20, 20, 20, 20)  # right, top, left, bottom

    def __init__(self, mapper):

        super().__init__()

        self.setLayout(QFormLayout())
        self.layout().setContentsMargins(*self.MARGINS)

        self.mapper = mapper

    def addBoundRow(self, node_path, widget, label=None):

        # WORKAROUND: Qt truncates the widget if it's a QCheckBox with its own
        # text unless we do this:
        if label is None:
            label = " "

        self.layout().addRow(label, widget)

        return self.mapper.bind(node_path, widget)
