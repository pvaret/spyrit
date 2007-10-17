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

from Singletons import singletons


class ActionSet:
  
  def __init__( s, parent ):
   
    config    = singletons.config
    
    s.parent  = parent
    
    s.actions = {
      "about":        ( "About %s..." % \
                         config._app_name, ":/app/icon",        None       ),
      "aboutqt":      ( "About Qt...",     ":/icon/qt-logo",    None       ),
      "newworld":     ( "New world...",    ":/icon/new_world", "Ctrl+N"    ),
      "quickconnect": ( "Quick connect...", None,               None       ),
      "quit":         ( "Quit",            ":/icon/quit",      "Ctrl+Q"    ),
      "closecurrent": ( "Close",           ":/icon/close",     "Ctrl+W"    ),
      "nexttab":      ( "Next Tab",         None,              "Shift+Tab" ),
      "previoustab":  ( "Previous Tab",     None,         "Shift+Ctrl+Tab" ),

      "connect":     ( "Connect",       None,         "Ctrl+Shift+S" ),
      "disconnect":  ( "Disconnect",    None,         "Ctrl+Shift+D" ),
      "historyup":   ( "History Up",   ":/icon/up",   "Ctrl+Up"      ),
      "historydown": ( "History Down", ":/icon/down", "Ctrl+Down"    ),
      "pageup":      ( "Page Up",      ":/icon/up",   "PgUp"    ),
      "pagedown":    ( "Page Down",    ":/icon/down", "PgDown"  ),
    }

    ## Very few actions have a specific role, so it's more effective to put
    ## roles in their own structure rather than in the one above.

    s.roles = {
      "about":   QtGui.QAction.AboutRole,
      "aboutqt": QtGui.QAction.AboutQtRole,
      "quit":    QtGui.QAction.QuitRole,
    }


  def bindAction( s, action, slot ):
    
    text, icon, shortcut = s.actions[ action ]
    
    if icon:
      a = QtGui.QAction( QtGui.QIcon( icon ), text, s.parent )
      
    else:
      a = QtGui.QAction( text, s.parent )
      
    if shortcut:
      a.setShortcut( QtGui.QKeySequence( shortcut ) )
    
    role = s.roles.get( action )
    
    if role:
      a.setMenuRole( role )
    
    connect( a, SIGNAL( "triggered()" ), slot )

    ## It is necessary to add the action to a widget before its shortcuts will
    ## work.
    s.parent.addAction( a )
    
    return a
    
    
  def allShortcuts( s ):
    
    return [ shortcut for text, icon, shortcut in s.actions.iteritems()
                                                            if shortcut ]
