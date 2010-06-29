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
from ConfigPaths import LOG_DIR
from Globals     import FORMAT_PROPERTIES
from Globals     import ANSI_COLORS as COL

from PlatformSpecific import PlatformSpecific

default_font = PlatformSpecific.default_font

DEFAULTS = (

  ( 'app_name',            u"Spyrit",    STR ),
  ( 'app_version',         u"0.4pre",    STR ),
  ( 'mainwindow_min_size', ( 320, 200 ), INTLIST ),
  ( 'mainwindow_pos',      None,         INTLIST ),
  ( 'worlds_section',      u"Worlds",    STR ),
  ( 'matches_section',     u"Matches",   STR ),

  ( 'widget_style',        None, STR ),

  ( 'name',                u"",   STR ),   ## Default name in config dialogs.
  ( 'host',                u"",   STR ),   ## Default host in config dialogs.
  ( 'port',                4201,  INT ),   ## Default port in config dialogs.
  ( 'ssl',                 False, BOOL ),  ## By default, no SSL on sockets.

  ( 'logfile_name',        u"[WORLDNAME]-%Y.%m.%d.log", STR ),
  ( 'logfile_dir',         LOG_DIR,                     STR ),
  ( 'autolog',             False,                       BOOL ),

  ( 'mainwindow_size',   ( 800, 600 ), INTLIST ),

  ( 'toolbar_icon_size', 24, INT ),

  ( 'output_font_name',        default_font, STR ),
  ( 'output_font_size',        0,            INT ),  ## 0 = Use system default.
  ( 'output_background_color', COL.black,    STR ),

  ( 'output_format',  { FORMAT_PROPERTIES.COLOR: COL.lightgray }, FORMAT ),

  ( 'world_encoding', u'latin1', STR ),

  ( 'split_scrollback', True, BOOL ),
  ( 'paging',           True, BOOL ),

  ( 'info_format', { FORMAT_PROPERTIES.COLOR: COL.darkgray,
                     FORMAT_PROPERTIES.ITALIC: True }, FORMAT ),

  ( 'input_font_name',        u"", STR ),  ## "" = Use system default.
  ( 'input_font_size',        0,   INT ),  ## 0 = Use system default.
  ( 'input_font_color',       u"", STR ),  ## "" = Use system default.
  ( 'input_background_color', u"white", STR ),  ## white

  ( 'splitter_sizes', [ 1000, 100, 100 ], INTLIST ),

  ( 'max_history_length', 0,    INT ), ## Unlimited.
  ( 'save_input_history', 10,   INT ),
  ( 'input_history',      [],   STRLIST ),

  ( 'shortcut_about',          None,               STR ),
  ( 'shortcut_aboutqt',        None,               STR ),
  ( 'shortcut_newworld',       u"Ctrl+N",          STR ),
  ( 'shortcut_quickconnect',   None,               STR ),
  ( 'shortcut_quit',           u"Ctrl+Q",          STR ),
  ( 'shortcut_nexttab',        u"Ctrl+PgDown",     STR ),
  ( 'shortcut_previoustab',    u"Ctrl+PgUp",       STR ),
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



DESCS = {

  'logfile_name': "default log filename pattern",
  'logfile_dir':  "default log directory",
  'autolog':      "start logging automatically on connect",

  'output_font_name':        "name of font in output window",
  'output_font_size':        "font size in output window",
  'output_background_color': "background color of output window",
  'output_format':           "format description for output window text",
  'info_format':             "format description for information text",

  'input_font_name':        "name of font in input field",
  'input_font_size':        "size of font in input field",
  'input_font_color':       "color of text in input field",
  'input_background_color': "background color of input field",

  'world_encoding': "server character encoding",

  'split_scrollback': "split output window when scrolling back",
  'paging':           "stop scrolling after one page of text",

  'save_input_history': "length of input history to keep between sessions",

  'shortcut_about':          "shortcut: About... dialog",
  'shortcut_aboutqt':        "shortcult: About Qt... dialog",
  'shortcut_newworld':       "shortcut: New World... dialog",
  'shortcut_quickconnect':   "shortcut: Quick Connect... dialog",
  'shortcut_quit':           "shortcut: quit the application",
  'shortcut_nexttab':        "shortcut: switch to the next tab",
  'shortcut_previoustab':    "shortcut: switch to the previous tab",
  'shortcut_close':          "shortcut: close the current tab",
  'shortcut_connect':        "shortcut: reconnect to the current world",
  'shortcut_disconnect':     "shortcut: disconnect from the current world",
  'shortcut_historyup':      "shortcut: previous entry in input history",
  'shortcut_historydown':    "shortcut: next entry in input history",
  'shortcut_autocomplete':   "shortcut: autocomplete current word in input field",
  'shortcut_pageup':         "shortcut: scroll one page up",
  'shortcut_pagedown':       "shortcut: scroll one page down",
  'shortcut_stepup':         "shortcut: scroll one line up",
  'shortcut_stepdown':       "shortcut: scroll one line down",
  'shortcut_home':           "shortcut: scroll to the beginning of output",
  'shortcut_end':            "shortcut: scroll to the end of output",
  'shortcut_startlog':       "shortcut: start logging output",
  'shortcut_stoplog':        "shortcut: stop logging output",
  'shortcut_toggle2ndinput': "shortcut: toggle secondary input field",

  'alert_on_activity': "animate taskbar when text is received from the server",

}


ALL_DEFAULTS = dict( ( k, v ) for ( k, v, t ) in DEFAULTS )
ALL_TYPES    = dict( ( k, t ) for ( k, v, t ) in DEFAULTS )
