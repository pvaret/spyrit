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
## ActionSet.py
##
## This holds the ActionSet class, which abstracts the QActions used by the
## software.
##

from PyQt4.QtCore import Qt
from PyQt4.QtGui  import QIcon
from PyQt4.QtGui  import QAction
from PyQt4.QtGui  import QKeySequence
from PyQt4.QtGui  import QApplication

from ConfigObserver import ConfigObserver


class ActionSet:

  def __init__( self, parent ):

    self.parent = parent

    config = QApplication.instance().core.config
    self.observer = ConfigObserver( config )
    self.closures = []

    self.actions = {

      ## Global actions

      "about":           ( u"About %s..." % \
                             config._app_name,    ":/app/icon"        ),
      "aboutqt":         ( u"About Qt...",        ":/icon/qt-logo"    ),
      "newworld":        ( u"New world...",       ":/icon/new_world"  ),
      "quickconnect":    ( u"Quick connect...",   None                ),
      "quit":            ( u"Quit",               ":/icon/quit"       ),
      "nexttab":         ( u"Next Tab",           None                ),
      "previoustab":     ( u"Previous Tab",       None                ),

      ## Per-world actions

      "close":           ( u"Close",              ":/icon/close"      ),
      "connect":         ( u"Connect",            ":/icon/connect"    ),
      "disconnect":      ( u"Disconnect",         ":/icon/disconnect" ),
      "historyup":       ( u"History up",         ":/icon/up"         ),
      "historydown":     ( u"History down",       ":/icon/down"       ),
      "autocomplete":    ( u"Autocomplete",       None                ),
      "pageup":          ( u"Page up",            ":/icon/up"         ),
      "pagedown":        ( u"Page down",          ":/icon/down"       ),
      "stepup":          ( u"Step up",            None                ),
      "stepdown":        ( u"Step down",          None                ),
      "home":            ( u"Home",               None                ),
      "end":             ( u"End",                None                ),
      "startlog":        ( u"Start log",          ":/icon/log_start"  ),
      "stoplog":         ( u"Stop log",           ":/icon/log_stop"   ),

      "toggle2ndinput":  ( u"Toggle secondary input", None            ),

    }

    ## Very few actions have a specific role, so it's more effective to put
    ## roles in their own structure rather than in the one above.

    self.roles = {
      "about":   QAction.AboutRole,
      "aboutqt": QAction.AboutQtRole,
      "quit":    QAction.QuitRole,
    }

    ## Likewise, custom shortcut contexts.

    self.contexts = {
      "historyup":    Qt.WidgetShortcut,
      "historydown":  Qt.WidgetShortcut,
      "autocomplete": Qt.WidgetShortcut,
    }


  def bindAction( self, action, slot ):

    text, icon = self.actions[ action ]

    a = QAction( text, self.parent )

    if icon: a.setIcon( QIcon( icon ) )

    shortcutname = "shortcut_" + action
    config = QApplication.instance().core.config

    def set_action_shortcut():

      ## Note how this closure uses 'config', 'a' and 'shortcutname' as bound
      ## variables.

      shortcut = config[ shortcutname ]

      if shortcut: a.setShortcut( QKeySequence( shortcut ) )
      else:        a.setShortcut( QKeySequence() )

    ## Call it once:
    set_action_shortcut()

    self.observer.addCallback( shortcutname, set_action_shortcut )

    ## Keep a reference to the closure, so it's not garbage-collected
    ## right away.
    self.closures.append( set_action_shortcut )

    role = self.roles.get( action )

    if role is not None:
      a.setMenuRole( role )

    context = self.contexts.get( action )

    if context is not None:
      a.setShortcutContext( context )

    a.triggered.connect( slot )

    ## It is necessary to add the action to a widget before its shortcuts will
    ## work.
    self.parent.addAction( a )

    return a


  def __del__( self ):

    self.observer = None
    self.closures = None
