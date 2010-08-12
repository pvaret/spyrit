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
  ( 'log_ansi',            False,                       BOOL ),

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


## Note: only the configuration keys with a description are listed by the
## configuration commands.

DESCRIPTIONS = {

  'logfile_name': u"default log filename pattern",
  'logfile_dir':  u"default log directory",
  'autolog':      u"start logging automatically on connect",
  'log_ansi':     u"use ANSI to log colors",

  'output_font_name':        u"name of font in output window",
  'output_font_size':        u"font size in output window",
  'output_background_color': u"background color of output window",
  'output_format':           u"format description for output window text",
  'info_format':             u"format description for information text",

  'input_font_name':        u"name of font in input field",
  'input_font_size':        u"size of font in input field",
  'input_font_color':       u"color of text in input field",
  'input_background_color': u"background color of input field",

  'world_encoding': u"server character encoding",

  'split_scrollback': u"split output window when scrolling back",
  'paging':           u"stop scrolling after one page of text",

  'save_input_history': u"length of input history to keep between sessions",

  'shortcut_about':          u"shortcut: About... dialog",
  'shortcut_aboutqt':        u"shortcut: About Qt... dialog",
  'shortcut_newworld':       u"shortcut: New World... dialog",
  'shortcut_quickconnect':   u"shortcut: Quick Connect... dialog",
  'shortcut_quit':           u"shortcut: quit the application",
  'shortcut_nexttab':        u"shortcut: switch to the next tab",
  'shortcut_previoustab':    u"shortcut: switch to the previous tab",
  'shortcut_close':          u"shortcut: close the current tab",
  'shortcut_connect':        u"shortcut: reconnect to the current world",
  'shortcut_disconnect':     u"shortcut: disconnect from the current world",
  'shortcut_historyup':      u"shortcut: previous entry in input history",
  'shortcut_historydown':    u"shortcut: next entry in input history",
  'shortcut_autocomplete':   u"shortcut: autocomplete current word in input field",
  'shortcut_pageup':         u"shortcut: scroll one page up",
  'shortcut_pagedown':       u"shortcut: scroll one page down",
  'shortcut_stepup':         u"shortcut: scroll one line up",
  'shortcut_stepdown':       u"shortcut: scroll one line down",
  'shortcut_home':           u"shortcut: scroll to the beginning of output",
  'shortcut_end':            u"shortcut: scroll to the end of output",
  'shortcut_startlog':       u"shortcut: start logging output",
  'shortcut_stoplog':        u"shortcut: stop logging output",
  'shortcut_toggle2ndinput': u"shortcut: toggle secondary input field",

  'alert_on_activity': u"animate taskbar when text is received from the server",

}


ALL_DEFAULTS = dict( ( k, v ) for ( k, v, t ) in DEFAULTS )
ALL_TYPES    = dict( ( k, t ) for ( k, v, t ) in DEFAULTS )
ALL_DESCS    = dict( ( k, DESCRIPTIONS[ k ] ) for ( k, _ , _ ) in DEFAULTS
                                              if k in DESCRIPTIONS )
