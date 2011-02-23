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
## TabDelegate.py
##
## Holds the TabDelegate class, a helper class which allows widgets contained
## in a QTabWidget to call QTabWidget methods that concern their own tab.
##


from localqt import *


class TabDelegate( QtCore.QObject ):

  DELEGATES = set([
                "removeTab",
                "isTabEnabled", "setTabEnabled",
                "tabIcon", "setTabIcon",
                "tabText", "setTabText",
                "tabToolTip", "setTabToolTip",
                "tabWhatsThis", "setTabWhatsThis",
              ])


  tabChanged = QtCore.pyqtSignal( bool )

  def __init__( s, widget ):

    QtCore.QObject.__init__( s )

    s.widget    = widget
    s.tabwidget = widget.parent()

    assert isinstance( s.tabwidget, QtGui.QTabWidget )

    s.is_current_tab = False

    s.tabwidget.currentChanged.connect( s.onTabChanged )


  @QtCore.pyqtSlot( int )
  def onTabChanged( s, i ):

    tabindex = s.tabwidget.indexOf( s.widget )

    is_now_current_tab = ( tabindex == i )

    if is_now_current_tab != s.is_current_tab:

      s.tabChanged.emit( is_now_current_tab )
      s.is_current_tab = is_now_current_tab


  def __getattr__( s, attr ):

    if not attr in s.DELEGATES:
      raise AttributeError( attr )

    ## Might raise AttributeError, which is okay:
    method = getattr( s.tabwidget, attr )

    tabindex = s.tabwidget.indexOf( s.widget )

    def delegated_method( *args ):
      return method( tabindex, *args )

    return delegated_method
