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
Provide the main UI of Spyrit, to be embedded in a tabbed container.
"""

from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState
from spyrit.ui.sliding_pane_container import SlidingPaneContainer
from spyrit.ui.welcome_pane import WelcomePane


class SpyritMainUIFactory:
    _settings: SpyritSettings
    _state: SpyritState

    def __init__(self, settings: SpyritSettings, state: SpyritState) -> None:
        self._settings = settings
        self._state = state

    def newUI(self) -> SlidingPaneContainer:
        ui = SlidingPaneContainer()
        ui.addPaneRight(WelcomePane(self._settings, self._state))
        return ui
