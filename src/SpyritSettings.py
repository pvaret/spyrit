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
## SpyritSettings.py
##
## Holds the definition of Spyrit settings.
##


import codecs

from Globals       import ANSI_COLORS as COL
from IniParser     import parse_settings
from Serializers   import Bool, Int, Str, List
from Serializers   import Size, Point, Format, Pattern, KeySequence
from SettingsPaths import SETTINGS_FILE, LOG_DIR, FILE_ENCODING

from settings.Settings import construct_proto

from PlatformSpecific import PlatformSpecific

default_font = PlatformSpecific.default_font


## World section name
WORLDS = u'worlds'

## Matches section name
MATCHES = u'matches'

## Schema for matches
MATCHES_SCHEMA = {
  'keys': (
    ( 'match',       { 'serializer': List( Pattern() ) } ),
    ( 'gag',         { 'serializer': Bool() } ),
    ( 'play',        { 'serializer': Str() } ),
    ( 'highlight',   { 'serializer': Format() } ),
    ( 'highlight_*', { 'serializer': Format() } ),
  )
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
    ( 'close',          { 'default': u"Ctrl+W" } ),
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
    ( 'name',         { 'serializer': Str(),  'default': None } ),
    ( 'net.encoding', { 'serializer': Str(),  'default': u"latin1" } ),
    ( 'net.host',     { 'serializer': Str(),  'default': u"" } ),
    ( 'net.port',     { 'serializer': Int(),  'default': 4201 } ),
    ( 'net.ssl',      { 'serializer': Bool(), 'default': False } ),
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
    ( 'ui.window.min_size',        { 'serializer': Size(),   'default': u"320x200" } ),
    ( 'ui.window.alert',           { 'serializer': Bool(),   'default': True } ),
    ( 'ui.toolbar.icon_size',      { 'serializer': Int(),    'default': 24 } ),
    ( 'ui.view.split_scroll',      { 'serializer': Bool(),   'default': True } ),
    ( 'ui.view.paging',            { 'serializer': Bool(),   'default': True } ),
    ( 'ui.view.font.name',         { 'serializer': Str(),    'default': default_font } ),
    ( 'ui.view.font.size',         { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.view.font.text_format',  { 'serializer': Format(), 'default': u"color: %s" % COL.lightgray } ),
    ( 'ui.view.font.info_format',  { 'serializer': Format(), 'default': u"italic ; color: %s" % COL.darkgray } ),
    ( 'ui.view.background.color',  { 'serializer': Str(),    'default': COL.black } ),
    ( 'ui.input.font.name',        { 'serializer': Str(),    'default': u"" } ),
    ( 'ui.input.font.size',        { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.input.font.color',       { 'serializer': Str(),    'default': u"" } ),
    ( 'ui.input.background.color', { 'serializer': Str(),    'default': COL.white } ),
    ( 'ui.input.max_history',      { 'serializer': Int(),    'default': 0 } ),
    ( 'ui.input.save_history',     { 'serializer': Int(),    'default': 10 } ),
  ),
  'sections': (
    (  MATCHES + u'.*', MATCHES_SCHEMA ),
    (  WORLDS + u'.*',  WORLDS_SCHEMA ),
    ( 'shortcuts',      SHORTCUTS_SCHEMA ),
  )
}

## Schema for stateful data that isn't really settings
STATE_SCHEMA = {
  'default_metadata': { 'state': True },
  'keys': (
    ( 'ui.window.pos',     { 'serializer': Point() } ),
    ( 'ui.window.size',    { 'serializer': Size(),        'default': u"800x600" } ),
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

  #'net.encoding': u"server character encoding",

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





def construct_settings():

  proto = construct_proto( [ SETTINGS_SCHEMA, STATE_SCHEMA ] )
  settings = proto.klass( None )
  settings.proto = proto

  return settings
