# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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
## Settings.py
##
## Holds the core settings object construction.
##


import codecs

from Globals       import ANSI_COLORS as COL
from IniParser     import ini_to_struct
from Serializers   import Bool, Int, Str, List
from Serializers   import Size, Point, Format, Pattern, KeySequence
from SettingsPaths import SETTINGS_FILE, LOG_DIR, FILE_ENCODING

from PlatformSpecific import PlatformSpecific

default_font = PlatformSpecific.default_font


## World section name
WORLDS = u'worlds'

## Matches section name
MATCHES = u'matches'

## Schema for matches
MATCHES_SCHEMA = {
  'keys': (
    ( 'match',       List( Pattern() ) ),
    ( 'gag',         Bool() ),
    ( 'play',        Str() ),
    ( 'highlight',   Format() ),
    ( 'highlight_*', Format() ),
  )
}

## Schema for keyboard shortcuts
SHORTCUTS_SCHEMA = {
  'keys': (
    ( 'about',          KeySequence( None ) ),
    ( 'aboutqt',        KeySequence( None ) ),
    ( 'newworld',       KeySequence( u"Ctrl+N" ) ),
    ( 'quickconnect',   KeySequence( None ) ),
    ( 'quit',           KeySequence( u"Ctrl+Q" ) ),
    ( 'nexttab',        KeySequence( u"Ctrl+PgDown" ) ),
    ( 'previoustab',    KeySequence( u"Ctrl+PgUp" ) ),
    ( 'close',          KeySequence( u"Ctrl+W" ) ),
    ( 'connect',        KeySequence( u"Ctrl+Shift+S" ) ),
    ( 'disconnect',     KeySequence( u"Ctrl+Shift+D" ) ),
    ( 'historyup',      KeySequence( u"Ctrl+Up" ) ),
    ( 'historydown',    KeySequence( u"Ctrl+Down" ) ),
    ( 'autocomplete',   KeySequence( u"Ctrl+Space" ) ),
    ( 'pageup',         KeySequence( u"PgUp" ) ),
    ( 'pagedown',       KeySequence( u"PgDown" ) ),
    ( 'stepup',         KeySequence( u"Ctrl+Shift+Up" ) ),
    ( 'stepdown',       KeySequence( u"Ctrl+Shift+Down" ) ),
    ( 'home',           KeySequence( u"Ctrl+Home" ) ),
    ( 'end',            KeySequence( u"Ctrl+End" ) ),
    ( 'startlog',       KeySequence( None ) ),
    ( 'stoplog',        KeySequence( None ) ),
    ( 'toggle2ndinput', KeySequence( u"Ctrl+M" ) ),
  )
}

## Schema for whole application and every world
SETTINGS_SCHEMA = {
  'keys': (
    ( 'app.name',                  Str( u"Spyrit" ) ),
    ( 'app.version',               Str( u"0.5dev" ) ),
    ( 'log.file',                  Str( u"[WORLDNAME]-%Y.%m.%d.log" ) ),
    ( 'log.dir',                   Str( LOG_DIR ) ),
    ( 'log.autostart',             Bool( u"off" ) ),
    ( 'log.ansi',                  Bool( u"off" ) ),
    ( 'ui.style',                  Str() ),
    ( 'ui.window.min_size',        Size( u"320x200" ) ),
    ( 'ui.window.alert',           Bool( u"on" ) ),
    ( 'ui.toolbar.icon_size',      Int( u"24" ) ),
    ( 'ui.view.split_scroll',      Bool( u"on" ) ),
    ( 'ui.view.paging',            Bool( u"on" ) ),
    ( 'ui.view.font.name',         Str( default_font ) ),
    ( 'ui.view.font.size',         Int( u"0" ) ),
    ( 'ui.view.font.text_format',  Format( u"color: %s" % COL.lightgray ) ),
    ( 'ui.view.font.info_format',  Format( u"italic ; color: %s" % COL.darkgray ) ),
    ( 'ui.view.background.color',  Str( COL.black ) ),
    ( 'ui.input.font.name',        Str( u"" ) ),
    ( 'ui.input.font.size',        Int( u"0" ) ),
    ( 'ui.input.font.color',       Str( u"" ) ),
    ( 'ui.input.background.color', Str( COL.white ) ),
    ( 'ui.input.max_history',      Int( u"0" ) ),
    ( 'ui.input.save_history',     Int( u"10" ) ),
    ( 'name',                      Str( None ) ),
    ( 'net.encoding',              Str( u"latin1" ) ),
    ( 'net.host',                  Str( u"" ) ),
    ( 'net.port',                  Int( u"4201" ) ),
    ( 'net.ssl',                   Bool( u"off" ) ),
  ),
  'sections': (
    (  MATCHES,    MATCHES_SCHEMA ),
    ( 'shortcuts', SHORTCUTS_SCHEMA ),
  )
}

## Schema for stateful data that isn't really settings
STATE_SCHEMA = {
  'keys': (
    ( 'ui.window.size',    Size( u"800x600" ) ),
    ( 'ui.window.pos',     Point() ),
    ( 'ui.splitter.sizes', List( Int(), u"1000, 100, 100" ) ),
    ( 'ui.input.history',  List( Str(), u"" ) ),
  ),
}


STATE_LABEL    = "DEFAULT_STATE"
SETTINGS_LABEL = "DEFAULT_SETTINGS"


DESCRIPTIONS = {

  'log.file':      u"default log filename pattern",
  'log.dir':       u"default log directory",
  'log.autostart': u"start logging automatically on connect",
  'log.ansi':      u"use ANSI to log colors",

  'ui.view.font.name':        u"name of font in output window",
  'ui.view.font.size':        u"font size in output window",
  'ui.view.font.text_format': u"format description for output window text",
  'ui.view.font.info_format': u"format description for information text",
  'ui.view.background.color': u"background color of output window",
  'ui.view.split_scroll':     u"split output window when scrolling back",
  'ui.view.paging':           u"stop scrolling after one page of text",

  'ui.input.font.name':        u"name of font in input field",
  'ui.input.font.size':        u"size of font in input field",
  'ui.input.font.color':       u"color of text in input field",
  'ui.input.background.color': u"background color of input field",
  'ui.input.save_history':     u"length of input history to keep between sessions",

  'ui.window.alert': u"animate taskbar when text is received from the server",

  'net.encoding': u"server character encoding",

  'shortcuts.about':          u"shortcut: About... dialog",
  'shortcuts.aboutqt':        u"shortcut: About Qt... dialog",
  'shortcuts.newworld':       u"shortcut: New World... dialog",
  'shortcuts.quickconnect':   u"shortcut: Quick Connect... dialog",
  'shortcuts.quit':           u"shortcut: quit the application",
  'shortcuts.nexttab':        u"shortcut: switch to the next tab",
  'shortcuts.previoustab':    u"shortcut: switch to the previous tab",
  'shortcuts.close':          u"shortcut: close the current tab",
  'shortcuts.connect':        u"shortcut: reconnect to the current world",
  'shortcuts.disconnect':     u"shortcut: disconnect from the current world",
  'shortcuts.historyup':      u"shortcut: previous entry in input history",
  'shortcuts.historydown':    u"shortcut: next entry in input history",
  'shortcuts.autocomplete':   u"shortcut: autocomplete current word in input field",
  'shortcuts.pageup':         u"shortcut: scroll one page up",
  'shortcuts.pagedown':       u"shortcut: scroll one page down",
  'shortcuts.stepup':         u"shortcut: scroll one line up",
  'shortcuts.stepdown':       u"shortcut: scroll one line down",
  'shortcuts.home':           u"shortcut: scroll to the beginning of output",
  'shortcuts.end':            u"shortcut: scroll to the end of output",
  'shortcuts.startlog':       u"shortcut: start logging output",
  'shortcuts.stoplog':        u"shortcut: stop logging output",
  'shortcuts.toggle2ndinput': u"shortcut: toggle secondary input field",

}





from SettingsNode          import SettingsNode
from SettingsSchema        import SettingsSchema
from SettingsNodeContainer import SettingsNodeContainer


def populate_from_struct( settings, struct, default_label ):

  keys, subsections = struct

  defaults = settings.getParentByLabel( default_label )

  if defaults:

    for k, v in keys.iteritems():

      s = defaults.getSerializer( k )

      if not s:
        ## This key doesn't exist in the schema. Move on.
        continue

      v = s.deserialize( v )
      if v is not None:
        settings[ k ] = v

  for k, subsection in subsections.iteritems():

    node = settings.section( k, create_if_missing=True )
    populate_from_struct( node, subsection, default_label )

  return settings



def construct_settings():

  settings         = SettingsNode()
  default_settings = SettingsSchema()
  default_state    = SettingsSchema()

  default_settings.setParent( default_state )
  settings.setParent( default_settings )

  default_state.label = STATE_LABEL
  default_state.loadDefinition( STATE_SCHEMA )

  default_settings.label = SETTINGS_LABEL
  default_settings.loadDefinition( SETTINGS_SCHEMA )

  ## TODO: Make this non-hardcoded.
  settings.sections[ WORLDS ] = SettingsNodeContainer( settings )
  settings.sections[ WORLDS ].new_sections_inherit_from = settings

  settings.sections[ MATCHES ] = SettingsNodeContainer( default_settings[ MATCHES ] )

  try:
    f = open( SETTINGS_FILE )
    ini = codecs.getreader( FILE_ENCODING )( f, "replace" ).read()

  except ( IOError, OSError ):
    pass

  else:
    populate_from_struct( settings, ini_to_struct( ini ), SETTINGS_LABEL )

  return settings
