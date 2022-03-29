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
# SettingsCommand.py
#
# Commands to manage the settings.
#


from typing import Any

from PyQt5.QtWidgets import QApplication

from Utilities import format_as_table
from .BaseCommand import BaseCommand
from SpyritSettings import DESCRIPTIONS


class SettingsCommand(BaseCommand):

    "View and modify the application settings."

    def _getSerializer(self, settings, setting):

        try:
            return settings.get(setting).proto.metadata.get("serializer")

        except KeyError:
            return None

    def _getValue(self, settings, setting):

        s = self._getSerializer(settings, setting)
        assert s is not None
        value = s.serialize(settings[setting])

        if value is None:
            value = "None"

        if " " in value:
            value = '"%s"' % value

        return value

    def _setValue(self, settings, setting, args):

        args = " ".join(args)

        s = self._getSerializer(settings, setting)

        if not s:
            return (False, "Unknown setting: %s" % setting)

        args = s.deserialize(args)
        settings[setting] = args

        return (True, None)

    def _resetValue(self, settings, setting):

        s = self._getSerializer(settings, setting)

        if not s:
            return (False, "Unknown setting: %s" % setting)

        try:
            del settings[setting]

        except KeyError:  # Playing it safe...
            pass

        return (True, None)

    def cmd_set(self, world, setting, *args):

        """
        Sets the given setting to the given value.

        Usage: %(cmd)s <setting> <value>

        Example: %(cmd)s ui.view.font.name "Courier New"

        """

        # TODO: Find a clean way to pass the settings.
        settings = QApplication.instance().core.settings  # type: ignore

        ok, msg = self._setValue(settings, setting, args)

        if ok:
            value = self._getValue(settings, setting)
            world.info("%s set to value %s" % (setting, value))

        else:
            world.info(msg)

    def cmd_worldset(self, world, setting, *args):

        """
        Sets the given setting to the given value, for this world only.

        Usage: %(cmd)s <setting> <value>

        Example: %(cmd)s ui.view.font.name "Courier New"

        """

        settings = world.settings

        ok, msg = self._setValue(settings, setting, args)

        if ok:
            value = self._getValue(settings, setting)
            world.info(
                "%s set to value %s on world %s"
                % (setting, value, world.title())
            )
        else:
            world.info(msg)

    def cmd_reset(self, world, setting):

        """
        Resets the given setting to its default value.

        Usage: %(cmd)s <setting>

        Example: %(cmd)s ui.view.font.name

        """

        # TODO: Find a clean way to pass the settings.
        settings = QApplication.instance().core.settings  # type: ignore

        ok, msg = self._resetValue(settings, setting)

        if ok:
            value = self._getValue(settings, setting)
            world.info("%s reset to value %s" % (setting, value))

        else:
            world.info(msg)

    def cmd_worldreset(self, world, setting):

        """
        Resets the given setting for this world to its global value.

        Usage: %(cmd)s <setting>

        Example: %(cmd)s ui.view.font.name

        """

        settings = world.settings

        ok, msg = self._resetValue(settings, setting)

        if ok:
            value = self._getValue(settings, setting)
            world.info(
                "%s reset to value %s on world %s"
                % (setting, value, world.title())
            )
        else:
            world.info(msg)

    def cmd_settings(self, world):

        """
        Lists all the available settings.

        Usage: %(cmd)s

        """

        max_len = max(len(k) for k in DESCRIPTIONS)

        output = "Available settings:\n"

        for setting, desc in sorted(DESCRIPTIONS.items()):
            output += setting.ljust(max_len + 2)
            output += desc
            output += "\n"

        world.info(output)

    def cmd_show(self, world, setting=None):

        """
        Show the current settings.

        Usage: %(cmd)s [<setting> | all]

        By default, only the values differing from the defaults are shown. If an
        optional setting argument is given, list all values for that setting
        (default, global, world.)

        If the optional argument 'all' is given, then all values for all
        settings are listed.

        Examples:
            %(cmd)s ui.view.font.name
            %(cmd)s all

        """

        worldsettings = world.settings
        # TODO: Find a clean way to pass the settings.
        settings = QApplication.instance().core.settings  # type: ignore

        # 1/ Retrieve list of settings to list, based on the argument given by
        # the user:

        if setting is not None:
            setting = setting.lower().strip()

        if (
            setting is None
        ):  # No argument given. Show only non-default settings.

            list_settings = []

            for k in sorted(DESCRIPTIONS):

                for context in (settings, worldsettings):

                    try:
                        if not context.get(k).isEmpty():
                            list_settings.append(k)
                            break

                    except KeyError:  # Happens if a key exists only on worlds.
                        pass

            if not list_settings:
                world.info("All the settings have default values.")
                return

        elif setting == "all":
            list_settings = sorted(DESCRIPTIONS)

        else:

            if self._getSerializer(settings, setting) is None:
                world.info("No such setting.")
                return

            list_settings = [setting]

        # 2/ Format and display as a table:

        output = "Current settings:\n"

        headers = ("Setting", "Defaults", "Global", "World")

        columns = [list_settings]

        DEFAULT: Any = object()  # marker for the case of default values.

        for node in (DEFAULT, settings, worldsettings):

            column = []

            for k in list_settings:

                s = self._getSerializer(
                    node if node is not DEFAULT else worldsettings, k
                )

                if s is None:
                    # The key doesn't exist in this context. This is likely a
                    # world-only key.
                    value = " "

                elif node is DEFAULT:
                    value = s.serialize(
                        worldsettings.get(k).proto.default_value
                    )

                else:
                    value = (
                        s.serialize(node[k])
                        if not node.get(k).isEmpty()
                        else "-"
                    )

                column.append(value if value else "None")

            columns.append(column)

        output += format_as_table(columns, headers)
        world.info(output)
