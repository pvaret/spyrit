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
Implements an application settings pane.
"""

from textwrap import TextWrapper
from typing import TypeVar, cast

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QFontMetrics, QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QLabel,
    QTabBar,
    QTabWidget,
    QStyle,
    QStyleOptionTab,
    QWidget,
)

from sunset import List, Settings

from spyrit import constants
from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.ui.base_dialog_pane import BaseDialogPane
from spyrit.ui.sizer import Sizer


_SettingsT = TypeVar("_SettingsT", bound=Settings)


def _root(settings: _SettingsT) -> _SettingsT:
    """
    Returns the topmost parent of the given settings object.

    Args:
        The settings object whose topmost parent should be returned.

    Returns:
        The topmost settings in the hierarchy.
    """

    if (parent := settings.parent()) is None:
        return settings
    return _root(parent)


def linewrap(
    text: str, line_length: int = constants.TAB_TEXT_WIDTH_CHARS
) -> str:
    """
    Wraps the given text to the given length.

    Args:
        text: The text to wrap.

        line_length: The length (in character counts) to which to wrap the text.

    Returns:
        The input text, wrapped.
    """

    wrapper = TextWrapper()
    wrapper.width = line_length

    return "\n".join(wrapper.wrap(text))


class _SideTabBar(QTabBar):
    """
    A QTabBar where the tabs are rotated 90 degrees.
    """

    def __init__(self) -> None:
        super().__init__()

        unit = Sizer(self).unitSize()

        self.setStyleSheet(
            f"QTabBar::tab {{ padding: {unit} {unit/1.5} {unit} {unit/1.5} }}"
        )

    def tabSizeHint(self, index: int) -> QSize:
        """
        Overrides the default tab size hint to rotate it 90 degrees, and account
        for labels that take multiple lines.

        Args:
            index: The index of the tab for which to produce a size hint.

        Returns:
            A size hint for the tab, rotated 90 degrees.
        """

        opt = QStyleOptionTab()
        self.initStyleOption(opt, index)

        metrics = cast(QFontMetrics, opt.fontMetrics)  # type: ignore
        label = cast(str, opt.text)  # type: ignore

        line_height = metrics.boundingRect(label).height()
        line_count = len(label.split("\n"))

        size = super().tabSizeHint(index).transposed()
        size.setHeight(size.height() + line_height * (line_count - 1))
        return size

    def paintEvent(self, arg__1: QPaintEvent) -> None:
        """
        Overrides the default paint event handler to render tabs rotated 90
        degrees.
        """

        del arg__1  # Unused.

        style = self.style()
        opt = QStyleOptionTab()
        painter = QPainter(self)

        for i in range(self.count()):
            self.initStyleOption(opt, i)

            # Draw the tab's frame.

            style.drawControl(
                QStyle.ControlElement.CE_TabBarTabShape, opt, painter
            )

            # Transpose the painter.

            painter.save()
            center = self.tabRect(i).center()
            painter.translate(center)
            painter.rotate(90)
            painter.translate(-center)

            # Transpose the text element's rect.
            # Ignore all the type errors because PySide6 types incorrectly omit
            # QStyleOptionTab.rect.

            rect = QRect()
            rect.setSize(opt.rect.size().transposed())  # type: ignore
            rect.moveCenter(opt.rect.center())  # type: ignore
            opt.rect = rect  # type: ignore

            # And render the text element.

            style.drawControl(
                QStyle.ControlElement.CE_TabBarTabLabel, opt, painter
            )
            painter.restore()


class SideTabWidget(QTabWidget):
    """
    A QTabWidget where the tabs are on the left side, and horizontal.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setTabBar(_SideTabBar())
        self.setTabPosition(QTabWidget.TabPosition.West)


class SettingsPane(BaseDialogPane):
    """
    An UI to configure all aspects of the application.

    Args:
        settings: The settings object to configure. This can be the
            application-global one, or one of the world-specific ones.
    """

    _settings: SpyritSettings
    _settings_ui: QWidget

    def __init__(
        self,
        settings: SpyritSettings,
    ) -> None:
        super().__init__()

        # Close the pane when the user clicks the "Ok" button.

        self.okClicked.connect(self.slideLeft)

        # Computes the list of all world settings, in alphabetical order,
        # starting with the toplevel, "All worlds" settings object.

        toplevel = _root(settings)

        worlds = sorted(
            toplevel.sections(),
            key=lambda settings: settings.name.get().strip().lower(),
        )

        # Create the main pane for the settings UI.

        pane_widget = SideTabWidget()

        # Global settings go here.

        pane_widget.addTab(
            self._appearanceSettingsUI(toplevel.ui), "Appearance"
        )
        pane_widget.addTab(
            self._shortcutsSettingsUI(toplevel.shortcuts), "Shortcuts"
        )

        # Per-world settings go here.

        for world in worlds:
            i = pane_widget.addTab(
                self._worldSettingsUi(world),
                linewrap("World: " + world.name.get().strip()),
            )
            if settings is world:
                pane_widget.setCurrentIndex(i)

        self.setWidget(pane_widget)

    def _appearanceSettingsUI(self, settings: SpyritSettings.UI) -> QWidget:
        """
        Constructs and returns a UI to manage appearance-related
        settings.

        Args:
            settings: The settings object to be managed from this UI.

        Returns:
            A UI to manage the given settings.
        """

        label = QLabel("Not implemented yet!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _shortcutsSettingsUI(
        self, settings: SpyritSettings.KeyShortcuts
    ) -> QWidget:
        """
        Constructs and returns a UI to manage the application's key shortcuts.

        Args:
            settings: The settings object to be managed from this UI.

        Returns:
            A UI to manage the application shortcuts.
        """

        label = QLabel("Not implemented yet!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _worldSettingsUi(self, settings: SpyritSettings) -> QWidget:
        """
        Constructs and returns a UI to manage the settings specific to a given
        world.

        Args:
            settings: The settings object to be managed from this UI.

        Returns:
            A UI to manage the given world's settings.
        """

        ui = QTabWidget()
        ui.setDocumentMode(True)
        ui.addTab(self._serverSettingsUI(settings.net), "Server")
        ui.addTab(self._triggersSettingsUI(settings.patterns), "Triggers")
        return ui

    def _serverSettingsUI(self, settings: SpyritSettings.Network) -> QWidget:
        """
        Constructs and returns a UI to manage a world's server settings.

        Args:
            settings: The settings object to be managed from this UI.

        Returns:
            A UI to manage the given settings.
        """

        label = QLabel("Not implemented yet!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _triggersSettingsUI(
        self, settings: List[SpyritSettings.Pattern]
    ) -> QWidget:
        """
        Constructs and returns a UI to manage a world's triggers.

        Args:
            settings: The settings object to be managed from this UI.

        Returns:
            A UI to manage the given settings.
        """

        label = QLabel("Not implemented yet!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label
