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
## ScrollableTabWidget.py
##
## Holds the ScrollableTabWidget class, which is a customized QTabWidget with
## feature such as tabs that react to the mouse wheel and a default page
## when no tab have been created yet.
##

from PyQt4.QtCore import QEvent
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui  import QTabBar
from PyQt4.QtGui  import QWidget
from PyQt4.QtGui  import QTabWidget
from PyQt4.QtGui  import QStackedWidget


class TabBarWheelEventHandler( QObject ):

  def eventFilter( self, tabbar, event ):

    if event.type() == QEvent.Wheel:

      if event.delta() < 0:
        tabbar.nextTab()

      else:
        tabbar.previousTab()

      return True

    else:
      return QObject.eventFilter( self, tabbar, event )


class ScrollableTabBar( QTabBar ):

  def __init__( self, parent=None ):

    QTabBar.__init__( self, parent )
    self.installEventFilter( TabBarWheelEventHandler( self ) )


  def nextTab( self ):

    if self.count() <= 1: return

    self.setCurrentIndex( ( self.currentIndex() + 1 ) % self.count() )


  def previousTab( self ):

    if self.count() <= 1: return

    self.setCurrentIndex( ( self.currentIndex() - 1 ) % self.count() )


class ScrollableTabWidget( QTabWidget ):

  numberOfTabChanged = pyqtSignal( int )

  def __init__( self, parent=None ):

    QTabWidget.__init__( self, parent )

    self.tabbar = ScrollableTabBar( self )
    self.setTabBar( self.tabbar )


  def tabInserted( self, i ):

    ## Ensures that the 'currentChanged( int )' signal is sent when the tab bar
    ## is modified, even if Qt doesn't think it should.

    self.currentChanged.emit( self.currentIndex() )
    self.numberOfTabChanged.emit( self.count() )


  def tabRemoved( self, i ):

    ## Ensures that the 'currentChanged( int )' signal is sent when the tab bar
    ## is modified, even if Qt doesn't think it should.

    self.currentChanged.emit( self.currentIndex() )
    self.numberOfTabChanged.emit( self.count() )



class SmartTabWidget( QStackedWidget ):

  def __init__( self, parent=None, fallback=None ):

    QStackedWidget.__init__( self, parent )

    self.tabwidget = ScrollableTabWidget( self )
    self.fallback  = fallback and fallback or QWidget( self )

    self.addWidget( self.tabwidget )
    self.addWidget( self.fallback )

    if fallback:
      self.setCurrentWidget( self.fallback )

    self.tabwidget.numberOfTabChanged.connect( self.switchView )


  @pyqtSlot( int )
  def switchView( self, tabcount ):

    current = self.tabwidget if tabcount > 0 else self.fallback
    self.setCurrentWidget( current )
