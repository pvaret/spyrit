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
## ScrollableTabWidget.py
##
## Holds the ScrollableTabWidget class, which is a customized QTabWidget with
## feature such as tabs that react to the mouse wheel.
##


from localqt import *

class TabBarWheelEventHandler( QtCore.QObject ):

  def eventFilter( s, tabbar, event ):

    if event.type() == QtCore.QEvent.Wheel \
       and isinstance( tabbar, QtGui.QTabBar ):

      if event.delta() < 0:
        tabbar.nextTab()

      else:
        tabbar.previousTab()

      return True

    else:
      return QtCore.QObject.eventFilter( s, tabbar, event )


class ScrollableTabBar( QtGui.QTabBar ):

  def __init__( s, *args ):
    
    QtGui.QTabBar.__init__( s, *args )
    s.installEventFilter( TabBarWheelEventHandler( s ) )
  
  def nextTab( s ):
    
    if s.count() <= 1:
      return
    
    s.setCurrentIndex( ( s.currentIndex() + 1 ) % s.count() )
    
    
  def previousTab( s ):
    
    if s.count() <= 1:
      return
    
    s.setCurrentIndex( ( s.currentIndex() - 1 ) % s.count() ) 
    
    
class ScrollableTabWidget( QtGui.QTabWidget ):

  def __init__( s, *args ):
    
    QtGui.QTabWidget.__init__( s, *args )
    
    s.tabbar = ScrollableTabBar( s )
    s.setTabBar( s.tabbar )
    
    connect( s, SIGNAL( "currentChanged ( int )" ), s.ensureTabFocus )
  
  
  def ensureTabFocus( s, i ):

    s.widget( i ).setFocus()
