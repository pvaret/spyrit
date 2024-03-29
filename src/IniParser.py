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
# IniParser.py
#
# Implements the loading and saving of settings.
#

"""
:doctest:

>>> from IniParser import *

"""


import re

from typing import Any, cast


RE_SECTION = re.compile(r"^(\[+)(.+?)(\]+)(.*)", re.UNICODE)
RE_KEYVALUE = re.compile(r"^(\w(?:[-.]?\w+)*)\s*=\s*(.*)", re.UNICODE)

INDENT = "  "

VERSION = 3


def replace_value(dict_, key_before, key_after):
    if key_before in dict_:
        if key_after is not None:
            dict_[key_after] = dict_[key_before]

        del dict_[key_before]


def update_settings_1_to_2(struct):
    REPLACE = [
        ("shortcut_about", "shortcuts.about"),
        ("shortcut_aboutqt", "shortcuts.aboutqt"),
        ("shortcut_newworld", "shortcuts.newworld"),
        ("shortcut_quickconnect", "shortcuts.quickconnect"),
        ("shortcut_quit", "shortcuts.quit"),
        ("shortcut_nexttab", "shortcuts.nexttab"),
        ("shortcut_previoustab", "shortcuts.previoustab"),
        ("shortcut_close", "shortcuts.closetab"),
        ("shortcut_connect", "shortcuts.connect"),
        ("shortcut_disconnect", "shortcuts.disconnect"),
        ("shortcut_historyup", "shortcuts.historyup"),
        ("shortcut_historydown", "shortcuts.historydown"),
        ("shortcut_autocomplete", "shortcuts.autocomplete"),
        ("shortcut_pageup", "shortcuts.pageup"),
        ("shortcut_pagedown", "shortcuts.pagedown"),
        ("shortcut_stepup", "shortcuts.stepup"),
        ("shortcut_stepdown", "shortcuts.stepdown"),
        ("shortcut_home", "shortcuts.home"),
        ("shortcut_end", "shortcuts.end"),
        ("shortcut_startlog", "shortcuts.startlog"),
        ("shortcut_stoplog", "shortcuts.stoplog"),
        ("shortcut_toggle2ndinput", "shortcuts.toggle2ndinput"),
        ("app_name", "app.name"),
        ("app_version", "app.version"),
        ("widget_style", "ui.style"),
        ("mainwindow_min_size", "ui.window.min_size"),
        ("mainwindow_pos", "ui.window.pos"),
        ("alert_on_activity", "ui.window.alert"),
        ("mainwindow_size", "ui.window.size"),
        ("toolbar_icon_size", "ui.toolbar.icon_size"),
        ("split_scrollback", "ui.view.split_scroll"),
        ("paging", "ui.view.paging"),
        ("info_format", "ui.view.font.info_format"),
        ("output_font_name", "ui.view.font.name"),
        ("output_font_size", "ui.view.font.size"),
        ("output_background_color", "ui.view.background.color"),
        ("output_format", "ui.view.font.text_format"),
        ("input_font_name", "ui.input.font.name"),
        ("input_font_size", "ui.input.font.size"),
        ("input_font_color", "ui.input.font.color"),
        ("input_background_color", "ui.input.background.color"),
        ("max_history_length", "ui.input.max_history"),
        ("save_input_history", "ui.input.save_history"),
        ("input_history", "ui.input.history"),
        ("splitter_sizes", "ui.splitter.sizes"),
        ("world_encoding", "net.encoding"),
        ("host", "net.host"),
        ("port", "net.port"),
        ("ssl", "net.ssl"),
        ("logfile_name", "log.file"),
        ("logfile_dir", "log.dir"),
        ("autolog", "log.autostart"),
        ("log_ansi", "log.ansi"),
        ("worlds_section", None),
        ("matches_section", None),
    ]

    keys, sections = struct
    worlds = sections.get("Worlds", (None, {}))[1]

    for from_, to in REPLACE:
        replace_value(keys, from_, to)

        for subsection in worlds.values():
            replace_value(subsection[0], from_, to)

    replace_value(sections, "Worlds", "worlds")
    replace_value(sections, "Matches", "matches")

    return struct


def update_settings_2_to_3(struct):
    """
    >>> match_struct = {
    ...   "match":          "match test",
    ...   "gag":            "gag test",
    ...   "play":           "play test",
    ...   "highlight":      "highlight test 1",
    ...   "highlight_test": "highlight test 2",
    ... }
    >>> struct = ( {}, {
    ...   "matches": ( {}, { "0": ( match_struct, {} ) } ),
    ...   "worlds": ( {}, {
    ...     "test world": ( {},
    ...                     { "matches": ( {},
    ...                                    { "0": ( match_struct, {} ) } ) } )
    ...   } )
    ... } )
    >>> struct = update_settings_2_to_3( struct )
    >>> expected_triggers_section = ( {}, { "1":
    ... ( {},
    ...   { "matches": ( { "1": "match test" }, {} ),
    ...     "actions": ( {
    ...         "gag": "gag test",
    ...         "play": "play test",
    ...       }, {
    ...         "highlights": ( {
    ...             "__line__": "highlight test 1",
    ...             "test": "highlight test 2",
    ...         }, {} ) } ) }
    ... ) } )
    >>> expected = ( {}, {
    ...   "worlds": ( {}, {
    ...     "test world": ( {}, { "triggers": expected_triggers_section } ) } ),
    ...   "triggers": expected_triggers_section,
    ... } )
    >>> struct == expected
    True

    """

    def update_matches(schema):
        from settings.Serializers import List, Str

        matches_keys: dict[str, str] = {}
        actions_keys: dict[str, str] = {}
        highlights_keys: dict[str, str] = {}
        new_schema = {
            "matches": (matches_keys, {}),
            "actions": (
                actions_keys,
                {"highlights": (highlights_keys, {})},
            ),
        }
        for k, v in schema[0].items():
            if k in ("gag", "play"):
                actions_keys[k] = v
            elif k.startswith("highlight"):
                if k == "highlight":
                    highlights_keys["__line__"] = v
                elif "_" in k:
                    _, k = k.split("_")
                    highlights_keys[k] = v
            elif k == "match":
                matches = List(Str()).deserialize(v)
                for i, v in enumerate(matches):
                    matches_keys[str(i + 1)] = v
        return ({}, new_schema)

    def update_all(struct):
        _, sections = struct

        if "matches" in sections:
            match_section = sections["matches"]
            new_trigger_sections = []
            for _, subsection in sorted(match_section[1].items()):
                new_trigger_sections.append(update_matches(subsection))
            del sections["matches"]
            sections["triggers"] = (
                {},
                {
                    str(i + 1): trigger_section
                    for i, trigger_section in enumerate(new_trigger_sections)
                },
            )

        for section, schema in sections.items():
            if section == "triggers":
                continue
            update_all(schema)

    update_all(struct)
    return struct


SETTINGS_UPDATERS = {
    1: (update_settings_1_to_2, 2),
    2: (update_settings_2_to_3, 3),
}


def parse_settings_version(text):
    # If not found, version is assumed to be the latest. This is not ideal, but
    # if we're not sure what version a given configuration file is, best not to
    # touch it.
    version = VERSION

    v = re.compile(r"^\#*\s*version\s*:\s*(?P<version>\d+)\s*$")

    # Look for version tag in first few lines:
    for i, line in enumerate(text.split("\n")):
        m = v.match(line)

        if m:
            version = int(m.group("version"))
            break

        if i > 2:  # Tag not found in first 3 lines...
            break

    return version


def parse_settings(text):
    version = parse_settings_version(text)
    struct = ini_to_struct(text)
    count = 0

    while version < VERSION and count <= len(SETTINGS_UPDATERS):
        count += 1

        if version in SETTINGS_UPDATERS:
            updater, version = SETTINGS_UPDATERS[version]
            struct = updater(struct)

        else:
            # Well, bummer, can't update struct. Return as is and hope for the
            # best.
            break

    return struct


def parse_ini_line(line):
    result = dict(key="", value="", section="", sectiondepth=0)

    line = line.strip()

    if line and line[0] in ("#", ";"):  # Line is a comment.
        return None

    m = RE_SECTION.match(line)

    if m:
        result["section"] = m.group(2).strip()
        result["sectiondepth"] = len(m.group(1))
        return result

    m = RE_KEYVALUE.match(line)

    if m:
        result["key"] = m.group(1)
        result["value"] = m.group(2).strip()
        return result

    return None


def ini_to_struct(ini_text):
    """
    Parses an ini-formatted block of text into a programmatically usable
    structure.

    >>> from pprint import pprint
    >>> input = r'''
    ...
    ... key1 = 1
    ... key2 = 2
    ...
    ... [ section1 ]
    ...
    ...   [[ subsection1 ]]
    ...     key3 = "This is a string"
    ...
    ...     [[[[ wrong_depth ]]]]
    ...       key4 = "Section has wrong depth and will be ignored"
    ...
    ... [ section2 ]
    ...   compound.key5 = 5
    ...
    ... '''
    >>> output = (
    ...   {"key1": "1", "key2": "2"},
    ...   {"section1": ({},
    ...                  {"subsection1": ({"key3": '"This is a string"'},
    ...                                   {})}),
    ...    "section2": ({"compound.key5": "5"}, {})})
    >>> output == ini_to_struct( input )
    True

    """

    KEYS, SECTIONS = 0, 1

    struct_type = tuple[dict[str, Any], dict[str, Any]]
    struct: struct_type = (
        {},  # keys
        {},  # subsections
    )
    current_struct = struct

    struct_stack: list[struct_type] = []
    skipsection = False

    for line in ini_text.split("\n"):
        result = parse_ini_line(line)

        if not result:
            continue

        key = cast(str, result["key"])
        section = cast(str, result["section"])

        if key and not skipsection:  # This is a key/value line.
            current_struct[KEYS][key] = result["value"]

        elif section:  # This is a section line.
            skipsection = False

            depth = cast(int, result["sectiondepth"])

            if depth > len(struct_stack) + 1:
                # Okay, this subsection is too deep, i.e. it looks something
                # like:
                #   [[ some section ]]
                #   ...
                #    [[[[ some subsection ]]]]
                # ... which is not good. So we skip it.
                skipsection = True
                continue

            while len(struct_stack) >= depth:
                current_struct = struct_stack.pop()

            current_struct[SECTIONS][section] = ({}, {})
            struct_stack.append(current_struct)
            current_struct = current_struct[SECTIONS][section]

    return struct


def struct_to_ini(struct, depth=0):
    """Takes a programmatic structure and generates its INI representation.

    The structure is a tuple of the form ( keys, sections ), where 'keys' and
    'sections' are both dictionaries. 'keys' associates setting names to values,
    both expressed as strings, and section associates section names to
    sub-structures of the same type as the parent structure.

    >>> keys = { "key1": "1", "key2": "2" }
    >>> sections = { "subsection": ( { "otherkey": "3" }, {} ) }
    >>> print( struct_to_ini( ( keys, sections ) ) )
    key1 = 1
    key2 = 2
    <BLANKLINE>
      [ subsection ]
      otherkey = 3
    <BLANKLINE>

    """

    output = ""

    keys, sections = struct

    for k, v in sorted(keys.items()):
        output += "%s%s = %s\n" % (INDENT * depth, k, v)

    depth += 1

    for k, substruct in sorted(sections.items()):
        output += "\n"
        output += INDENT * depth
        output += "[" * depth
        output += " %s " % k
        output += "]" * depth
        output += "\n"
        output += struct_to_ini(substruct, depth)

    return output
