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
## TabWidget.py
##
## Holds our QTabWidget customizations.
##

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui  import QWidget
from PyQt4.QtGui  import QTabWidget
from PyQt4.QtGui  import QStackedWidget


class TabWidget( QTabWidget ):
  "A QTabWidget with a few added features."

  numberOfTabChanged = pyqtSignal( int )

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


  def previousTab( self ):

    i = self.currentIndex()
    if i > 0:
      self.setCurrentIndex( i-1 )


  def nextTab( self ):

    i = self.currentIndex()
    if i < self.count()-1:
      self.setCurrentIndex( i+1 )


class FallbackTabWidget( QStackedWidget ):
  """A widget that takes a tabwidget and a fallback widget and displays the
  latter when the former has no tab."""

  def __init__( self, parent=None, tabwidget=None, fallback=None ):

    QStackedWidget.__init__( self, parent )

    if fallback is None:
        fallback = QWidget( parent )

    if tabwidget is None:
        tabwidget = TabWidget( parent )

    assert isinstance( tabwidget, TabWidget )

    self.tabwidget = tabwidget
    self.fallback  = fallback

    self.addWidget( self.tabwidget )
    self.addWidget( self.fallback )

    self.setCurrentWidget( self.fallback )

    self.tabwidget.numberOfTabChanged.connect( self.switchView )


  @pyqtSlot( int )
  def switchView( self, tabcount ):

    current = self.tabwidget if tabcount > 0 else self.fallback
    self.setCurrentWidget( current )
