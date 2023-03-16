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
# SpyritSettings.py
#
# Holds the definition of Spyrit settings.
#


import codecs

from typing import Sequence

from PyQt6.QtCore import QSize

from Globals import ANSI_COLORS as COL
from Globals import SOLARIZED
from IniParser import parse_settings
from IniParser import struct_to_ini
from IniParser import VERSION
from PlatformSpecific import PlatformSpecific
from SettingsPaths import FILE_ENCODING
from SettingsPaths import LOG_DIR
from SettingsPaths import SETTINGS_FILE
from SettingsPaths import SETTINGS_FILE_CANDIDATES
from SettingsPaths import STATE_FILE
from SettingsPaths import STATE_FILE_CANDIDATES
from settings.Serializers import Bool
from settings.Serializers import Format
from settings.Serializers import Int
from settings.Serializers import KeySequence
from settings.Serializers import List
from settings.Serializers import Pattern
from settings.Serializers import Point
from settings.Serializers import Size
from settings.Serializers import Str
from settings.Settings import Settings


default_font = PlatformSpecific.default_font


def for_all_keys(key_schema):
    return {"keys": (("*", key_schema),)}


def for_all_sections(section_schema):
    return {"sections": (("*", section_schema),)}


# Section names.
WORLDS = "worlds"
TRIGGERS = "triggers"
MATCHES = "matches"
ACTIONS = "actions"
SHORTCUTS = "shortcuts"


# Schema for matches
TRIGGERS_SCHEMA = {
    "keys": (("name", {"serializer": Str(), "default": None}),),
    "sections": (
        (MATCHES, for_all_keys({"serializer": Pattern()})),
        (
            ACTIONS,
            {
                "keys": (
                    ("gag", {"serializer": Bool()}),
                    ("play", {"serializer": Str()}),
                    ("link", {"serializer": Str()}),
                ),
                "sections": (
                    ("highlights", for_all_keys({"serializer": Format()})),
                ),
            },
        ),
    ),
}


# Schema for keyboard shortcuts
SHORTCUTS_SCHEMA = {
    "default_metadata": {"serializer": KeySequence()},
    "keys": (
        ("about", {"default": None}),
        ("aboutqt", {"default": None}),
        ("newworld", {"default": "Ctrl+N"}),
        ("quickconnect", {"default": None}),
        ("quit", {"default": "Ctrl+Q"}),
        ("nexttab", {"default": "Ctrl+PgDown"}),
        ("previoustab", {"default": "Ctrl+PgUp"}),
        ("closetab", {"default": "Ctrl+W"}),
        ("connect", {"default": "Ctrl+Shift+S"}),
        ("disconnect", {"default": "Ctrl+Shift+D"}),
        ("historyup", {"default": "Ctrl+Up"}),
        ("historydown", {"default": "Ctrl+Down"}),
        ("autocomplete", {"default": "Ctrl+Space"}),
        ("pageup", {"default": "PgUp"}),
        ("pagedown", {"default": "PgDown"}),
        ("stepup", {"default": "Ctrl+Shift+Up"}),
        ("stepdown", {"default": "Ctrl+Shift+Down"}),
        ("home", {"default": "Ctrl+Home"}),
        ("end", {"default": "Ctrl+End"}),
        ("startlog", {"default": None}),
        ("stoplog", {"default": None}),
        ("toggle2ndinput", {"default": "Ctrl+M"}),
    ),
}

# Schema for whole application and every world
WORLDS_SCHEMA = {
    "keys": (
        ("name", {"serializer": Str(), "default": None}),
        ("net.encoding", {"serializer": Str(), "default": "latin1"}),
        ("net.host", {"serializer": Str(), "default": ""}),
        ("net.login_script", {"serializer": Str(), "default": None}),
        ("net.port", {"serializer": Int(), "default": 4201}),
        ("net.ssl", {"serializer": Bool(), "default": False}),
        ("net.keepalive_seconds", {"serializer": Int(), "default": 0}),
        ("net.keepalive_packet", {"serializer": Str(), "default": "\x00"}),
    ),
    "inherit": "..",
}

SETTINGS_SCHEMA = {
    "keys": (
        ("app.name", {"serializer": Str(), "default": "Spyrit"}),
        ("app.version", {"serializer": Str(), "default": "0.5dev"}),
        (
            "log.file",
            {"serializer": Str(), "default": "[WORLDNAME]-%Y.%m.%d.log"},
        ),
        ("log.dir", {"serializer": Str(), "default": LOG_DIR}),
        ("log.autostart", {"serializer": Bool(), "default": False}),
        ("log.ansi", {"serializer": Bool(), "default": False}),
        ("ui.style", {"serializer": Str(), "default": False}),
        ("ui.window.min_size", {"serializer": Size(), "default": "640x480"}),
        ("ui.window.alert", {"serializer": Bool(), "default": True}),
        ("ui.toolbar.icon_size", {"serializer": Int(), "default": 24}),
        ("ui.view.split_scroll", {"serializer": Bool(), "default": True}),
        ("ui.view.paging", {"serializer": Bool(), "default": True}),
        ("ui.view.font.name", {"serializer": Str(), "default": default_font}),
        ("ui.view.font.size", {"serializer": Int(), "default": 0}),
        (
            "ui.view.font.text_format",
            {"serializer": Format(), "default": "color: %s" % COL.lightgray},
        ),
        (
            "ui.view.font.info_format",
            {
                "serializer": Format(),
                "default": "italic ; color: %s" % COL.darkgray,
            },
        ),
        (
            "ui.view.background.color",
            {"serializer": Str(), "default": COL.black},
        ),
        ("ui.view.wrap_column", {"serializer": Int(), "default": 0}),
        ("ui.input.font.name", {"serializer": Str(), "default": ""}),
        ("ui.input.font.size", {"serializer": Int(), "default": 0}),
        ("ui.input.font.color", {"serializer": Str(), "default": ""}),
        (
            "ui.input.background.color",
            {"serializer": Str(), "default": SOLARIZED.base3},
        ),
        ("ui.input.max_history", {"serializer": Int(), "default": 0}),
        ("ui.input.save_history", {"serializer": Int(), "default": 10}),
    ),
    "sections": (
        (TRIGGERS, for_all_sections(TRIGGERS_SCHEMA)),
        (WORLDS, for_all_sections(WORLDS_SCHEMA)),
        (SHORTCUTS, SHORTCUTS_SCHEMA),
    ),
}

# Schema for stateful data that isn't really settings
STATE_SCHEMA = {
    "keys": (
        ("ui.window.pos", {"serializer": Point()}),
        ("ui.window.size", {"serializer": Size(), "default": QSize(1200, 900)}),
    ),
    "sections": (
        (
            WORLDS,
            for_all_sections(
                {
                    "keys": (
                        (
                            "ui.splitter.sizes",
                            {
                                "serializer": List(Int()),
                                "default": [1000, 100, 100],
                            },
                        ),
                        (
                            "ui.input.history",
                            {"serializer": List(Str()), "default": ""},
                        ),
                    ),
                    "inherit": "..",
                }
            ),
        ),
    ),
}


DESCRIPTIONS = {
    "log.file": "default log filename pattern",
    "log.dir": "default log directory",
    "log.autostart": "start logging automatically on connect",
    "log.ansi": "use ANSI to log colors",
    "ui.view.font.name": "name of font in output window",
    "ui.view.font.size": "font size in output window",
    "ui.view.font.text_format": "format description for output window text",
    "ui.view.font.info_format": "format description for information text",
    "ui.view.background.color": "background color of output window",
    "ui.view.split_scroll": "split output window when scrolling back",
    "ui.view.paging": "stop scrolling after one page of text",
    "ui.input.font.name": "name of font in input field",
    "ui.input.font.size": "size of font in input field",
    "ui.input.font.color": "color of text in input field",
    "ui.input.background.color": "background color of input field",
    "ui.input.save_history": "length of input history to keep between sessions",
    "ui.window.alert": "animate taskbar when text is received from the server",
    "net.encoding": "server character encoding",
    "net.login_script": "arbitrary text to send on connect",
    SHORTCUTS + ".about": "shortcut: About... dialog",
    SHORTCUTS + ".aboutqt": "shortcut: About Qt... dialog",
    SHORTCUTS + ".newworld": "shortcut: New World... dialog",
    SHORTCUTS + ".quickconnect": "shortcut: Quick Connect... dialog",
    SHORTCUTS + ".quit": "shortcut: quit the application",
    SHORTCUTS + ".nexttab": "shortcut: switch to the next tab",
    SHORTCUTS + ".previoustab": "shortcut: switch to the previous tab",
    SHORTCUTS + ".closetab": "shortcut: close the current tab",
    SHORTCUTS + ".connect": "shortcut: reconnect to the current world",
    SHORTCUTS + ".disconnect": "shortcut: disconnect from the current world",
    SHORTCUTS + ".historyup": "shortcut: previous entry in input history",
    SHORTCUTS + ".historydown": "shortcut: next entry in input history",
    SHORTCUTS + ".autocomplete": "shortcut: autocomplete current word",
    SHORTCUTS + ".pageup": "shortcut: scroll one page up",
    SHORTCUTS + ".pagedown": "shortcut: scroll one page down",
    SHORTCUTS + ".stepup": "shortcut: scroll one line up",
    SHORTCUTS + ".stepdown": "shortcut: scroll one line down",
    SHORTCUTS + ".home": "shortcut: scroll to the beginning of output",
    SHORTCUTS + ".end": "shortcut: scroll to the end of output",
    SHORTCUTS + ".startlog": "shortcut: start logging output",
    SHORTCUTS + ".stoplog": "shortcut: stop logging output",
    SHORTCUTS + ".toggle2ndinput": "shortcut: toggle secondary input field",
}


def find_and_read(file_candidates, encoding=FILE_ENCODING):
    for filename in file_candidates:
        try:
            reader = codecs.getreader(encoding)
            return reader(open(filename, "rb"), "ignore").read()

        except (LookupError, IOError, OSError):
            pass

    return None, ""


def _load(schema, candidates: Sequence[str]):
    settings = Settings()
    settings.loadSchema(schema)

    settings_text = find_and_read(candidates)

    settings_struct = parse_settings(settings_text)
    settings.restore(settings_struct)

    return settings


def load_settings():
    return _load(SETTINGS_SCHEMA, SETTINGS_FILE_CANDIDATES)


def load_state():
    return _load(STATE_SCHEMA, STATE_FILE_CANDIDATES)


def _save(settings, filename: str):
    settings_text = "# version: %d\n" % (VERSION) + struct_to_ini(
        settings.dump()
    )

    try:
        writer = codecs.getwriter(FILE_ENCODING)
        writer(open(filename, "wb"), "ignore").write(settings_text)

    except (LookupError, IOError, OSError):
        # Well shucks.
        pass


def save_settings(settings):
    _save(settings, SETTINGS_FILE)


def save_state(state):
    _save(state, STATE_FILE)
