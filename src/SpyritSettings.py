# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## SpyritSettings.py
##
## Holds the definition of Spyrit settings.
##


import codecs

from Globals       import ANSI_COLORS as COL
from IniParser     import parse_settings, struct_to_ini, VERSION
from Serializers   import Bool, Int, Str, List
from Serializers   import Size, Point, Format, Pattern, KeySequence
from SettingsPaths import SETTINGS_FILE, STATE_FILE, LOG_DIR, FILE_ENCODING
from SettingsPaths import SETTINGS_FILE_CANDIDATES, STATE_FILE_CANDIDATES

from settings.Settings import Settings

from PlatformSpecific import PlatformSpecific


default_font = PlatformSpecific.default_font


def for_all_keys( key_schema ):
  return { 'keys': ( ( u'*', key_schema ), ) }

def for_all_sections( section_schema ):
  return { 'sections': ( ( u'*', section_schema ), ) }


## Section names.
WORLDS    = u'worlds'
TRIGGERS  = u'triggers'
MATCHES   = u'matches'
ACTIONS   = u'actions'
SHORTCUTS = u'shortcuts'

## Schema for matches
TRIGGERS_SCHEMA = {
  'keys': (
    ( 'name', { 'serializer': Str(), 'default': None } ),
  ),
  'sections': (
    ( MATCHES, for_all_keys( { 'serializer': Pattern() } ) ),

    ( ACTIONS, {
        'keys': (
          ( 'gag',  { 'serializer': Bool() } ),
          ( 'play', { 'serializer': Str() } ),
          ( 'link', { 'serializer': Str() } ),
        ),
        'sections': (
          ( 'highlights', for_all_keys( { 'serializer': Format() } ) ),
        ),
      }
    ),
  ),
}


## Schema for keyboard shortcuts
SHORTCUTS_SCHEMA = {
  'default_metadata': { 'serializer': KeySequence() },
  'keys': (
    ( 'about',          { 'default': None } ),
    ( 'aboutqt',        { 'default': None } ),
    ( 'newworld',       { 'default': u"Ctrl+N" } ),
    ( 'quickconnect',   { 'default': None } ),
    ( 'quit',           { 'default': u"Ctrl+Q" } ),
    ( 'nexttab',        { 'default': u"Ctrl+PgDown" } ),
    ( 'previoustab',    { 'default': u"Ctrl+PgUp" } ),
    ( 'closetab',       { 'default': u"Ctrl+W" } ),
    ( 'connect',        { 'default': u"Ctrl+Shift+S" } ),
    ( 'disconnect',     { 'default': u"Ctrl+Shift+D" } ),
    ( 'historyup',      { 'default': u"Ctrl+Up" } ),
    ( 'historydown',    { 'default': u"Ctrl+Down" } ),
    ( 'autocomplete',   { 'default': u"Ctrl+Space" } ),
    ( 'pageup',         { 'default': u"PgUp" } ),
    ( 'pagedown',       { 'default': u"PgDown" } ),
    ( 'stepup',         { 'default': u"Ctrl+Shift+Up" } ),
    ( 'stepdown',       { 'default': u"Ctrl+Shift+Down" } ),
    ( 'home',           { 'default': u"Ctrl+Home" } ),
    ( 'end',            { 'default': u"Ctrl+End" } ),
    ( 'startlog',       { 'default': None } ),
    ( 'stoplog',        { 'default': None } ),
    ( 'toggle2ndinput', { 'default': u"Ctrl+M" } ),
  )
}

## Schema for whole application and every world
WORLDS_SCHEMA = {
  'keys': (
    ( 'name',             { 'serializer': Str(),  'default': None } ),
    ( 'net.encoding',     { 'serializer': Str(),  'default': u"latin1" } ),
    ( 'net.host',         { 'serializer': Str(),  'default': u"" } ),
    ( 'net.login_script', { 'serializer': Str(),  'default': None } ),
    ( 'net.port',         { 'serializer': Int(),  'default': 4201 } ),
    ( 'net.ssl',          { 'serializer': Bool(), 'default': False } ),
  ),
  'inherit': '..',
}

SETTINGS_SCHEMA = {
  'keys': (
    ( 'app.name',                  { 'serializer': Str(),    'default': u"Spyrit" } ),
    ( 'app.version',               { 'serializer': Str(),    'default': u"0.5dev" } ),
    ( 'log.file',                  { 'serializer': Str(),    'default': u"[WORLDNAME]-%Y.%m.%d.log" } ),
    ( 'log.dir',                   { 'serializer': Str(),    'default': LOG_DIR } ),
    ( 'log.autostart',             { 'serializer': Bool(),   'default': False } ),
    ( 'log.ansi',                  { 'serializer': Bool(),   'default': False } ),
    ( 'ui.style',                  { 'serializer': Str(),    'default': False } ),
    ( 'ui.window.min_size',        { 'serializer': Size(),   'default': u"640x480" } ),
    ( 'ui.window.alert',           { 'serializer': Bool(),   'default': True } ),
    ( 'ui.toolbar.icon_size',      { 'serializer': Int(),    'default': 24 } ),
    ( 'ui.view.split_scroll',      { 'serializer': Bool(),   'default': True } ),
    ( 'ui.view.paging',            { 'serializer': Bool(),   'default': True } ),
    ( 'ui.view.font.name',         { 'serializer': Str(),    'default': default_font } ),
    ( 'ui.view.font.size',         { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.view.font.text_format',  { 'serializer': Format(), 'default': u"color: %s" % COL.lightgray } ),
    ( 'ui.view.font.info_format',  { 'serializer': Format(), 'default': u"italic ; color: %s" % COL.darkgray } ),
    ( 'ui.view.background.color',  { 'serializer': Str(),    'default': COL.black } ),
    ( 'ui.view.wrap_column',       { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.input.font.name',        { 'serializer': Str(),    'default': u"" } ),
    ( 'ui.input.font.size',        { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.input.font.color',       { 'serializer': Str(),    'default': u"" } ),
    ( 'ui.input.background.color', { 'serializer': Str(),    'default': COL.white } ),
    ( 'ui.input.max_history',      { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.input.save_history',     { 'serializer': Int(),    'default': 10 } ),
  ),
  'sections': (
    ( TRIGGERS, for_all_sections( TRIGGERS_SCHEMA ) ),
    ( WORLDS,   for_all_sections( WORLDS_SCHEMA ) ),
    ( SHORTCUTS, SHORTCUTS_SCHEMA ),
  )
}

## Schema for stateful data that isn't really settings
STATE_SCHEMA = {
  'default_metadata': { 'exclude_from_dump': True },
  'keys': (
    ( 'ui.window.pos',     { 'serializer': Point() } ),
    ( 'ui.window.size',    { 'serializer': Size(),        'default': u"1200x900" } ),
    ( 'ui.splitter.sizes', { 'serializer': List( Int() ), 'default': [ 1000, 100, 100 ] } ),
    ( 'ui.input.history',  { 'serializer': List( Str() ), 'default': u"" } ),
  ),
}


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

  'net.encoding':     u"server character encoding",
  'net.login_script': u"arbitrary text to send on connect",

  SHORTCUTS + '.about':          u"shortcut: About... dialog",
  SHORTCUTS + '.aboutqt':        u"shortcut: About Qt... dialog",
  SHORTCUTS + '.newworld':       u"shortcut: New World... dialog",
  SHORTCUTS + '.quickconnect':   u"shortcut: Quick Connect... dialog",
  SHORTCUTS + '.quit':           u"shortcut: quit the application",
  SHORTCUTS + '.nexttab':        u"shortcut: switch to the next tab",
  SHORTCUTS + '.previoustab':    u"shortcut: switch to the previous tab",
  SHORTCUTS + '.closetab':       u"shortcut: close the current tab",
  SHORTCUTS + '.connect':        u"shortcut: reconnect to the current world",
  SHORTCUTS + '.disconnect':     u"shortcut: disconnect from the current world",
  SHORTCUTS + '.historyup':      u"shortcut: previous entry in input history",
  SHORTCUTS + '.historydown':    u"shortcut: next entry in input history",
  SHORTCUTS + '.autocomplete':   u"shortcut: autocomplete current word",
  SHORTCUTS + '.pageup':         u"shortcut: scroll one page up",
  SHORTCUTS + '.pagedown':       u"shortcut: scroll one page down",
  SHORTCUTS + '.stepup':         u"shortcut: scroll one line up",
  SHORTCUTS + '.stepdown':       u"shortcut: scroll one line down",
  SHORTCUTS + '.home':           u"shortcut: scroll to the beginning of output",
  SHORTCUTS + '.end':            u"shortcut: scroll to the end of output",
  SHORTCUTS + '.startlog':       u"shortcut: start logging output",
  SHORTCUTS + '.stoplog':        u"shortcut: stop logging output",
  SHORTCUTS + '.toggle2ndinput': u"shortcut: toggle secondary input field",

}


def find_and_read( file_candidates, encoding=FILE_ENCODING ):
  for filename in file_candidates:
    try:
      reader = codecs.getreader( encoding )
      return filename, reader( open( filename, 'rb' ), 'ignore' ).read()

    except ( LookupError, IOError, OSError ):
      pass

  return None, u""


def load_settings():
  settings = Settings()
  settings.loadSchema( SETTINGS_SCHEMA )
  settings.loadSchema( STATE_SCHEMA )

  found_settings_file, settings_text = find_and_read( SETTINGS_FILE_CANDIDATES )

  settings_struct = parse_settings( settings_text )
  settings.restore( settings_struct )

  found_state_file, state_text = find_and_read( STATE_FILE_CANDIDATES )

  state_struct = parse_settings( state_text )
  settings.restore( state_struct )

  return settings


def save_settings( settings ):

  settings_text = "## version: %d\n" % ( VERSION ) \
                + struct_to_ini( settings.dump() )

  try:
    writer = codecs.getwriter( FILE_ENCODING )
    writer( open( SETTINGS_FILE, 'wb' ), 'ignore' ).write( settings_text )

  except ( LookupError, IOError, OSError ):
    ## Well shucks.
    pass


  ## Only dump the 'state' part of the structure.
  dump_predicate = lambda node: node.proto.metadata.get( "schema_id" ) == id( STATE_SCHEMA )
  state_text = "## version: %d\n" % ( VERSION ) \
             + struct_to_ini( settings.dump( dump_predicate ) )

  try:
    writer = codecs.getwriter( FILE_ENCODING )
    writer( open( STATE_FILE, 'wb' ), 'ignore' ).write( state_text )

  except ( LookupError, IOError, OSError ):
    ## Well shucks too.
    pass
