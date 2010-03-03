# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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
## Defaults.py
##
## Contains the default configuration items.
##

from ConfigTypes import *
from FormatData  import FORMAT_PROPERTIES
from ConfigPaths import LOG_DIR


DEFAULTS = (

  ( 'app_name',            u"Spyrit",    STR ),
  ( 'app_version',         u"0.4pre",    STR ),
  ( 'mainwindow_min_size', ( 320, 200 ), INTLIST ),
  ( 'mainwindow_pos',      None,         INTLIST ),
  ( 'worlds_section',      u"Worlds",    STR ),

  ( 'widget_style',        None, STR ),

  ( 'name',                u"",   STR ),   ## Default name in config dialogs.
  ( 'host',                u"",   STR ),   ## Default host in config dialogs.
  ( 'port',                4201,  INT ),   ## Default port in config dialogs.
  ( 'ssl',                 False, BOOL ),  ## By default, no SSL on sockets.

  ( 'logfile_name',        u"[WORLDNAME]-%Y.%m.%d.log", STR ),
  ( 'logfile_dir',         LOG_DIR,                     STR ),
  ( 'autolog',             False,                       BOOL ),

  ( 'show_splashscreen', False,        BOOL ),
  ( 'mainwindow_size',   ( 800, 600 ), INTLIST ),

  ( 'toolbar_icon_size', 24, INT ),

  ( 'output_font_name',        u"Courier", STR ),
  ( 'output_font_size',        0,          INT ),  ## 0 = Use system default.
  ( 'output_background_color', u"black", STR ),

  ( 'output_format',  { FORMAT_PROPERTIES.COLOR: u"lightGrey" }, FORMAT ),

  ( 'world_encoding', u'latin1', STR ),

  ( 'split_scrollback', True, BOOL ),
  ( 'paging',           True, BOOL ),

  ( 'info_format', { FORMAT_PROPERTIES.COLOR: u"darkGray",
                     FORMAT_PROPERTIES.ITALIC: True }, FORMAT ),

  ( 'input_font_name',        u"", STR ),  ## "" = Use system default.
  ( 'input_font_size',        0,   INT ),  ## 0 = Use system default.
  ( 'input_font_color',       u"", STR ),  ## "" = Use system default.
  ( 'input_background_color', u"white", STR ),  ## white

  ( 'splitter_sizes', [ 1000, 100, 100 ], INTLIST ),

  ( 'input_command_char', u"/", STR ),
  ( 'max_history_length', 0,    INT ), ## Unlimited.
  ( 'save_input_history', 10,   INT ),
  ( 'input_history',      [],   STRLIST ),

  ( 'shortcut_about',          None,               STR ),
  ( 'shortcut_aboutqt',        None,               STR ),
  ( 'shortcut_newworld',       u"Ctrl+N",          STR ),
  ( 'shortcut_quickconnect',   None,               STR ),
  ( 'shortcut_quit',           u"Ctrl+Q",          STR ),
  ( 'shortcut_nexttab',        u"Shift+Tab",       STR ),
  ( 'shortcut_previoustab',    u"Shift+Ctrl+Tab",  STR ),
  ( 'shortcut_close',          u"Ctrl+W",          STR ),
  ( 'shortcut_connect',        u"Ctrl+Shift+S",    STR ),
  ( 'shortcut_disconnect',     u"Ctrl+Shift+D",    STR ),
  ( 'shortcut_historyup',      u"Ctrl+Up",         STR ),
  ( 'shortcut_historydown',    u"Ctrl+Down",       STR ),
  ( 'shortcut_autocomplete',   u"Tab",             STR ),
  ( 'shortcut_pageup',         u"PgUp",            STR ),
  ( 'shortcut_pagedown',       u"PgDown",          STR ),
  ( 'shortcut_stepup',         u"Ctrl+Shift+Up",   STR ),
  ( 'shortcut_stepdown',       u"Ctrl+Shift+Down", STR ),
  ( 'shortcut_home',           u"Ctrl+Home",       STR ),
  ( 'shortcut_end',            u"Ctrl+End",        STR ),

  ( 'shortcut_startlog',       None,               STR ),
  ( 'shortcut_stoplog',        None,               STR ),

  ( 'shortcut_toggle2ndinput', u"Ctrl+M",          STR ),

  ( 'alert_on_activity', True, BOOL ),

)


MATCHES_SECTION = "matches"

AUTOTYPES = (
  ( MATCHES_SECTION, STR ),
)
