# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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

from Types import *


DEFAULTS = (

  ( 'app_name',            "Spyrit",     STR ),
  ( 'app_version',         "0.3pre",     STR ),
  ( 'mainwindow_min_size', ( 320, 200 ), INTLIST ),
  ( 'mainwindow_pos',      None,         INTLIST ),
  ( 'worlds_section',      "Worlds",     STR ),

  ( 'widget_style',        None, STR ),

  ( 'name',                "",    STR ),   ## Default name in config dialogs.
  ( 'host',                "",    STR ),   ## Default host in config dialogs.
  ( 'port',                4201,  INT ),   ## Default port in config dialogs.
  ( 'ssl',                 False, BOOL ),  ## By default, no SSL on sockets.

  ( 'show_splashscreen', False,        BOOL ),
  ( 'mainwindow_size',   ( 800, 600 ), INTLIST ),

  ( 'toolbar_icon_size', 24, INT ),

  ( 'output_font_name',        "Courier", STR ),
  ( 'output_font_size',        0,         INT ),  ## 0 = Use system default.
  ( 'output_font_color',       "#c0c0c0", STR ),  ## light grey
  ( 'output_background_color', "#000000", STR ),  ## black

  ( 'output_scrollback_overlay', True, BOOL ),

  ( 'bold_as_highlight', True, BOOL ),

  ( 'info_font_color',   "#606060", STR ),  ## dark grey

  ( 'input_font_name',        "", STR ),  ## "" = Use system default.
  ( 'input_font_size',        0,  INT ),  ## 0 = Use system default.
  ( 'input_font_color',       "", STR ),  ## "" = Use system default.
  ( 'input_background_color', "#ffffff", STR ),  ## white

  ( 'splitter_sizes', [ 1000, 100, 100 ], INTLIST ),

  ( 'input_command_char', "/", STR ),
  ( 'max_history_length', 0,   INT ), ## Unlimited.
  ( 'save_input_history', 10,  INT ),
  ( 'input_history',      [],  STRLIST ),

  ( 'shortcut_about',        None,             STR ),
  ( 'shortcut_aboutqt',      None,             STR ),
  ( 'shortcut_newworld',     "Ctrl+N",         STR ),
  ( 'shortcut_quickconnect', None,             STR ),
  ( 'shortcut_quit',         "Ctrl+Q",         STR ),
  ( 'shortcut_nexttab',      "Shift+Tab",      STR ),
  ( 'shortcut_previoustab',  "Shift+Ctrl+Tab", STR ),
  ( 'shortcut_close',        "Ctrl+W",         STR ),
  ( 'shortcut_connect',      "Ctrl+Shift+S",   STR ),
  ( 'shortcut_disconnect',   "Ctrl+Shift+D",   STR ),
  ( 'shortcut_historyup',    "Ctrl+Up",        STR ),
  ( 'shortcut_historydown',  "Ctrl+Down",      STR ),
  ( 'shortcut_pageup',       "PgUp",           STR ),
  ( 'shortcut_pagedown',     "PgDown",         STR ),

  ( 'alert_on_activity',  True, BOOL ),

)
