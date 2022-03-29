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
# SettingsWidgetMapper.py
#
# Implements automatic mapping between a settings node and configuration
# widgets.
#


from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QCheckBox


def qlineedit_not_empty(qlineedit: QLineEdit):
    return len(qlineedit.text()) > 0


class BaseWidgetMapper(QObject):

    widget_class: Any = None
    widget_value_setter = None
    widget_signal_name: str = "--UNSET--"
    widget_value_class: Any = None
    settings_value_class: Any = None

    valueChanged = pyqtSignal(object)

    def __init__(self, widget):

        super().__init__()

        self.widget = widget
        self.widget_signal = getattr(widget, self.widget_signal_name)
        self.widget_signal.connect(self.emitValueChanged)
        self.validator = None

    @pyqtSlot(int)
    @pyqtSlot(bool)
    @pyqtSlot(str)
    def emitValueChanged(self, widget_value):

        assert isinstance(widget_value, self.widget_value_class)
        settings_value = self.widgetToSettingsValue(widget_value)
        assert isinstance(settings_value, self.settings_value_class)

        self.valueChanged.emit(settings_value)

    def setValue(self, settings_value):

        if settings_value is None or self.widget_value_setter is None:
            return

        assert isinstance(settings_value, self.settings_value_class)
        widget_value = self.settingsToWidgetValue(settings_value)
        assert isinstance(widget_value, self.widget_value_class)

        self.widget_value_setter(self.widget, widget_value)

    @staticmethod
    def widgetToSettingsValue(value):

        return value

    @staticmethod
    def settingsToWidgetValue(value):

        return value

    def setValidator(self, validator):

        self.validator = validator

    def validate(self):

        if not self.validator:
            return True  # Default: no validator means everything validates.

        return self.validator(self.widget)

    def __hash__(self):

        return id(self)


class QLineEditMapper(BaseWidgetMapper):

    widget_class = QLineEdit
    widget_value_setter = QLineEdit.setText
    widget_signal_name = "textEdited"
    widget_value_class = str
    settings_value_class = str

    @staticmethod
    def widgetToSettingsValue(value):

        return str(value)

    @staticmethod
    def settingsToWidgetValue(value):

        return str(value)


class QSpinBoxMapper(BaseWidgetMapper):

    widget_class = QSpinBox
    widget_value_setter = QSpinBox.setValue
    widget_signal_name = "valueChanged"
    widget_value_class = int
    settings_value_class = int


class QCheckBoxMapper(BaseWidgetMapper):

    widget_class = QCheckBox
    widget_value_setter = QCheckBox.setCheckState
    widget_signal_name = "stateChanged"
    widget_value_class = int
    settings_value_class = bool

    @staticmethod
    def widgetToSettingsValue(value):

        return value == Qt.CheckState.Checked

    @staticmethod
    def settingsToWidgetValue(value):

        return Qt.CheckState.Checked if value else Qt.CheckState.Unchecked


def get_mapper(widget):

    if isinstance(widget, BaseWidgetMapper):
        return widget

    mappers = [QLineEditMapper, QSpinBoxMapper, QCheckBoxMapper]

    for mapper in mappers:
        if isinstance(widget, mapper.widget_class):
            return mapper(widget)

    raise NotImplementedError(
        "No mapper found for %s!" % widget.__class__.__name__
    )


class SettingsWidgetMapper(QObject):

    settingsValid = pyqtSignal(bool)
    settingsEmpty = pyqtSignal(bool)

    def __init__(self, settings):

        super().__init__()

        self.settings = settings
        self.option_path_for_widget = {}

    def bind(self, option_path, widget):

        widget_mapper = get_mapper(widget)
        self.option_path_for_widget[widget_mapper] = option_path

        widget_mapper.valueChanged.connect(self.updateSettingsValue)
        widget_mapper.setValue(self.settings[option_path])

        return widget_mapper

    def updateSettingsValue(self, value):

        widget_mapper = self.sender()

        if isinstance(widget_mapper, BaseWidgetMapper):
            if widget_mapper.validate():

                option_path = self.option_path_for_widget[widget_mapper]
                self.settings[option_path] = value

            self.emitSignals()

    def emitSignals(self):

        empty = self.settings.isEmpty()
        valid = all(mapper.validate() for mapper in self.option_path_for_widget)

        self.settingsEmpty.emit(empty)
        self.settingsValid.emit(valid)
