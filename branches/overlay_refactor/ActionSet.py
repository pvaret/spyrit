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
## ActionSet.py
##
## This holds the ActionSet class, which abstracts the QActions used by the
## software.
##

from localqt    import *

from Singletons     import singletons
from ConfigObserver import ConfigObserver


class ActionSet:
  
  def __init__( s, parent ):
   
    s.parent  = parent

    config     = singletons.config
    s.observer = ConfigObserver( config )
    
    s.actions = {

      ## Global actions

      "about":        ( "About %s..." % \
                         config._app_name,  ":/app/icon"       ),
      "aboutqt":      ( "About Qt...",      ":/icon/qt-logo"   ),
      "newworld":     ( "New world...",     ":/icon/new_world" ),
      "quickconnect": ( "Quick connect...", None               ),
      "quit":         ( "Quit",             ":/icon/quit"      ),
      "nexttab":      ( "Next Tab",         None               ),
      "previoustab":  ( "Previous Tab",     None               ),

      ## Per-world actions

      "close":       ( "Close",        ":/icon/close"      ),
      "connect":     ( "Connect",      ":/icon/connect"    ),
      "disconnect":  ( "Disconnect",   ":/icon/disconnect" ),
      "historyup":   ( "History Up",   ":/icon/up"         ),
      "historydown": ( "History Down", ":/icon/down"       ),
      "pageup":      ( "Page Up",      ":/icon/up"         ),
      "pagedown":    ( "Page Down",    ":/icon/down"       ),

    }

    ## Very few actions have a specific role, so it's more effective to put
    ## roles in their own structure rather than in the one above.

    s.roles = {
      "about":   QtGui.QAction.AboutRole,
      "aboutqt": QtGui.QAction.AboutQtRole,
      "quit":    QtGui.QAction.QuitRole,
    }


  def bindAction( s, action, slot ):
    
    text, icon = s.actions[ action ]
    
    if icon:
      a = QtGui.QAction( QtGui.QIcon( icon ), text, s.parent )
      
    else:
      a = QtGui.QAction( text, s.parent )

    shortcutname = "shortcut_" + action

    def set_action_shortcut():

      ## Note how this closure uses 'a' and 'shortcutname' as bound variables.

      shortcut = singletons.config[ shortcutname ]

      if shortcut: a.setShortcut( QtGui.QKeySequence( shortcut ) )
      else:        a.setShortcut( QtGui.QKeySequence() )
     
    s.observer.addCallback( shortcutname, set_action_shortcut )

    set_action_shortcut()  ## Set the shortcut at least once!

    role = s.roles.get( action )
    
    if role:
      a.setMenuRole( role )
    
    connect( a, SIGNAL( "triggered()" ), slot )

    ## It is necessary to add the action to a widget before its shortcuts will
    ## work.
    s.parent.addAction( a )
    
    return a
