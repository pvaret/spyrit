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


from Serializers  import Bool, Int, Str, List
from Serializers  import Size, Point, Format, Pattern, KeySequence
from ConfigPaths  import LOG_DIR
from Globals      import ANSI_COLORS as COL

from PlatformSpecific import PlatformSpecific

default_font = PlatformSpecific.default_font

## World section name
WORLDS = 'worlds'

## Schema for individual worlds
WORLDS_SCHEMA = {
  'keys': (
    ( '/name',         Str( None ) ),
    ( '/net/encoding', Str( u"latin1" ) ),
    ( '/net/host',     Str( u"" ) ),
    ( '/net/port',     Int( u"4201" ) ),
    ( '/net/ssl',      Bool( u"off" ) ),
  ),
  'inherit': '/',
}

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
    ( '/app/name',                  Str( u"Spyrit" ) ),
    ( '/app/version',               Str( u"0.5dev" ) ),
    ( '/log/file',                  Str( u"[WORLDNAME]-%Y.%m.%d.log" ) ),
    ( '/log/dir',                   Str( LOG_DIR ) ),
    ( '/log/autostart',             Bool( u"off" ) ),
    ( '/log/ansi',                  Bool( u"off" ) ),
    ( '/ui/style',                  Str() ),
    ( '/ui/window/min_size',        Size( u"320x200" ) ),
    ( '/ui/window/alert',           Bool( u"on" ) ),
    ( '/ui/toolbar/icon_size',      Int( u"24" ) ),
    ( '/ui/view/split_scroll',      Bool( u"on" ) ),
    ( '/ui/view/paging',            Bool( u"on" ) ),
    ( '/ui/view/font/name',         Str( default_font ) ),
    ( '/ui/view/font/size',         Int( u"0" ) ),
    ( '/ui/view/font/text_format',  Format( u"color: %s" % COL.lightgray ) ),
    ( '/ui/view/font/info_format',  Format( u"italic ; color: %s" % COL.darkgray ) ),
    ( '/ui/view/background/color',  Str( COL.black ) ),
    ( '/ui/input/font/name',        Str( u"" ) ),
    ( '/ui/input/font/size',        Int( u"0" ) ),
    ( '/ui/input/font/color',       Str( u"" ) ),
    ( '/ui/input/background/color', Str( COL.white ) ),
    ( '/ui/input/max_history',      Int( u"0" ) ),
    ( '/ui/input/save_history',     Int( u"10" ) ),
  ),
  'sections': (
    ( '/%s' % WORLDS, WORLDS_SCHEMA ),
    ( '/matches',     MATCHES_SCHEMA ),
    ( '/shortcuts',   SHORTCUTS_SCHEMA ),
  )
}

## Schema for stateful data that isn't really settings
STATE_SCHEMA = {
  'keys': (
    ( '/ui/window/size', Size( u"800x600" ) ),
    ( '/ui/window/pos',  Point() ),
  ),
  'sections': (
    ( '/worlds', {
        'keys': (
          ( '/ui/splitter/sizes', List( Int(), u"1000, 100, 100" ) ),
          ( '/ui/input/history',  List( Str(), [] ) ),
        ),
    } ),
  ),
}



from SettingsNode   import SettingsNode
from SettingsSchema import SettingsSchema

def construct_settings():

  settings         = SettingsNode()
  default_settings = SettingsSchema()
  default_state    = SettingsSchema()

  default_settings.setParent( default_state )
  settings.setParent( default_settings )

  default_state.loadDefinition( STATE_SCHEMA )
  default_settings.loadDefinition( SETTINGS_SCHEMA )

  return settings
