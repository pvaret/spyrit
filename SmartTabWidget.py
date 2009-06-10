# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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
## feature such as tabs that react to the mouse wheel and a default page
## when no tab have been created yet.
##


from localqt import *


class TabBarWheelEventHandler( QtCore.QObject ):

  def eventFilter( s, tabbar, event ):

    if event.type() == QtCore.QEvent.Wheel:

      if event.delta() < 0:
        tabbar.nextTab()

      else:
        tabbar.previousTab()

      return True

    else:
      return QtCore.QObject.eventFilter( s, tabbar, event )


class ScrollableTabBar( QtGui.QTabBar ):

  def __init__( s, parent=None ):
    
    QtGui.QTabBar.__init__( s, parent )
    s.installEventFilter( TabBarWheelEventHandler( s ) )
  

  def nextTab( s ):
    
    if s.count() <= 1: return
    
    s.setCurrentIndex( ( s.currentIndex() + 1 ) % s.count() )
    
    
  def previousTab( s ):
    
    if s.count() <= 1: return
    
    s.setCurrentIndex( ( s.currentIndex() - 1 ) % s.count() ) 
    
    
class ScrollableTabWidget( QtGui.QTabWidget ):

  def __init__( s, parent=None ):
    
    QtGui.QTabWidget.__init__( s, parent )
    
    s.tabbar = ScrollableTabBar( s )
    s.setTabBar( s.tabbar )


  def tabInserted( s, i ):
 
    ## Ensures that the 'currentChanged( int )' signal is sent when the tab bar
    ## is modified, even if Qt doesn't think it should.
 
    s.emit( SIGNAL( "currentChanged ( int )" ), s.currentIndex() )
    s.emit( SIGNAL( "numberOfTabChanged( int )" ), s.count() )


  def tabRemoved( s, i ):

    ## Ensures that the 'currentChanged( int )' signal is sent when the tab bar
    ## is modified, even if Qt doesn't think it should.

    s.emit( SIGNAL( "currentChanged ( int )" ), s.currentIndex() )
    s.emit( SIGNAL( "numberOfTabChanged( int )" ), s.count() )



class SmartTabWidget( QtGui.QStackedWidget ):

  def __init__( s, parent=None, fallback=None ):
    
    QtGui.QStackedWidget.__init__( s, parent )

    s.tabwidget = ScrollableTabWidget( s )
    s.fallback  = fallback and fallback or QtGui.QWidget( s )

    s.addWidget( s.tabwidget )
    s.addWidget( s.fallback )

    if fallback: s.setCurrentWidget( s.fallback )

    connect( s.tabwidget, SIGNAL( "numberOfTabChanged( int )" ), s.switchView )


  def switchView( s, tabcount ):

    if tabcount > 0: s.setCurrentWidget( s.tabwidget )
    else:            s.setCurrentWidget( s.fallback )
