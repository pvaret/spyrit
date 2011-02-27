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
## WorldUI.py
##
## Contains the WorldUI class, which manages a world's widget for reading and
## writing.
##


from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QTimeLine
from PyQt4.QtGui  import QIcon
from PyQt4.QtGui  import QStyle
from PyQt4.QtGui  import QToolBar
from PyQt4.QtGui  import QSplitter
from PyQt4.QtGui  import QTabWidget
from PyQt4.QtGui  import QMessageBox
from PyQt4.QtGui  import QApplication

from ActionSet          import ActionSet
from TabDelegate        import TabDelegate
from WorldInputUI       import WorldInputUI
from Autocompleter      import Autocompleter
from OutputManager      import OutputManager
from SingleShotTimer    import SingleShotTimer
from SplittableTextView import SplittableTextView
from pipeline           import ChunkData

class LED:

  def __init__( self ):

    self.CONNECTED_UNLIT    = QIcon( ":/icon/unlit_green_led" )
    self.CONNECTED_LIT      = QIcon( ":/icon/lit_green_led" )
    self.DISCONNECTED_UNLIT = QIcon( ":/icon/unlit_red_led" )
    self.DISCONNECTED_LIT   = QIcon( ":/icon/lit_red_led" )


  def select( self, connected, lit ):

    if connected:
      return lit and self.CONNECTED_LIT or self.CONNECTED_UNLIT

    else:
      return lit and self.DISCONNECTED_LIT or self.DISCONNECTED_UNLIT



class WorldUI( QSplitter ):

  def __init__( self, tabwidget, world ):

    QSplitter.__init__( self, Qt.Vertical, tabwidget )

    assert isinstance( tabwidget, QTabWidget )

    self.world = world
    self.led   = LED()

    self.tab = TabDelegate( self )

    self.tab.tabChanged.connect( self.onTabChanged )

    self.blinker = QTimeLine( 200, self ) ## ms
    self.blinker.setFrameRange( 0, 3 )
    self.blinker.frameChanged.connect( self.iconBlink )
    self.blinker.finished.connect( self.steadyIcon )

    self.world.socketpipeline.addSink( self.startIconBlink,
                                       ChunkData.PACKETBOUND | ChunkData.NETWORK )

    self.alert_timer = SingleShotTimer( self.windowAlert )

    ## Setup input and output UI.

    self.outputui = SplittableTextView( self )
    self.addWidget( self.outputui )

    self.outputui.setFocusProxy( self )

    self.output_manager = OutputManager( world, self.outputui )

    self.inputui = WorldInputUI( self, world )
    self.addWidget( self.inputui )

    self.secondaryinputui = WorldInputUI( self, world, shouldsavehistory=False )
    self.addWidget( self.secondaryinputui )
    self.secondaryinputui.hide()

    self.inputui.returnPressed.connect( self.outputui.pingPage )
    self.secondaryinputui.returnPressed.connect( self.outputui.pingPage )

    self.world.socketpipeline.pipeline.flushBegin.connect(
                              self.output_manager.textcursor.beginEditBlock )

    self.world.socketpipeline.pipeline.flushEnd.connect(
                              self.output_manager.textcursor.endEditBlock )

    self.world.socketpipeline.pipeline.flushEnd.connect( self.outputui.repaint )

    world.socketpipeline.addSink( self.output_manager.processChunk,
                                    ChunkData.TEXT
                                  | ChunkData.FLOWCONTROL
                                  | ChunkData.NETWORK )

    world.socketpipeline.addSink( self.output_manager.textformatmanager.processChunk,
                                    ChunkData.ANSI
                                  | ChunkData.HIGHLIGHT )

    self.setFocusProxy( self.inputui )

    self.inputui.focusChanged.connect( self.setFocusProxy )
    self.secondaryinputui.focusChanged.connect( self.setFocusProxy )

    ## Setup autocompleter.

    self.autocompleter = Autocompleter()
    world.socketpipeline.addSink( self.autocompleter.sink )

    ## Setup splitter.

    self.setChildrenCollapsible( False )
    self.setSizes( world.conf._splitter_sizes )

    self.splitterMoved.connect( self.saveSplitterPosition )

    ## Create toolbar and bind World-related actions.

    self.toolbar = QToolBar()
    self.toolbar.setMovable( False )
    self.toolbar.setFloatable( False )
    self.toolbar.setContextMenuPolicy( Qt.PreventContextMenu )
    self.toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )

    self.toolbar.setWindowTitle( world.title() )

    self.actionset = ActionSet( self )

    self.actionset.bindAction( "stepup",   self.outputui.stepUp )
    self.actionset.bindAction( "stepdown", self.outputui.stepDown )
    self.actionset.bindAction( "pageup",   self.outputui.pageUp )
    self.actionset.bindAction( "pagedown", self.outputui.pageDown )
    self.actionset.bindAction( "home",     self.outputui.moveScrollbarToTop )
    self.actionset.bindAction( "end",      self.outputui.moveScrollbarToBottom )

    self.actionset.bindAction( "toggle2ndinput", self.toggleSecondaryInput )

    connect_action    = self.actionset.bindAction( "connect",
                                                   self.world.connectToWorld )

    disconnect_action = self.actionset.bindAction( "disconnect",
                                                   self.world.disconnectFromWorld )

    connect_action.setEnabled( False )
    disconnect_action.setEnabled( False )

    startlog_action = self.actionset.bindAction( "startlog",
                                                 self.world.startLogging )

    stoplog_action  = self.actionset.bindAction( "stoplog",
                                                 self.world.stopLogging )

    startlog_action.setEnabled( True )
    stoplog_action.setEnabled( False )


    world.disconnected.connect( connect_action.setEnabled )
    world.disconnected.connect( disconnect_action.setDisabled )


    world.nowLogging.connect( startlog_action.setDisabled )
    world.nowLogging.connect( stoplog_action.setEnabled )

    self.toolbar.addAction( connect_action )
    self.toolbar.addAction( disconnect_action )

    self.toolbar.addAction(
      self.actionset.bindAction( "close", self.close )
    )

    self.toolbar.addSeparator()

    self.toolbar.addAction( startlog_action )
    self.toolbar.addAction( stoplog_action )

    self.toolbar.addSeparator()

    self.world.setUI( self )

    for line in QApplication.instance().core.motd:
      self.world.info( line )


  def updateToolBarIcons( self, size ):

    if not size:
      size = QApplication.style().pixelMetric( QStyle.PM_ToolBarIconSize )

    new_size = QSize( size, size )
    self.toolbar.setIconSize( new_size )


  def toggleSecondaryInput( self ):

    if self.secondaryinputui.isHidden():
      self.secondaryinputui.show()
      self.secondaryinputui.setFocus()

    else:
      self.secondaryinputui.hide()
      self.inputui.setFocus()


  @pyqtSlot( bool )
  def onTabChanged( self, is_now_visible ):

    if is_now_visible:

      ## Ensure the currently visible world has focus.
      self.setFocus()
      self.steadyIcon()


  def startIconBlink( self, chunk ):

    ## Don't blink if already blinking:

    if self.blinker.state() != QTimeLine.NotRunning:
      return

    self.blinker.start()
    self.alert_timer.start()


  @pyqtSlot( int )
  def iconBlink( self, frame ):

    if not self.world:
      return

    led = self.led.select( connected = self.world.isConnected(),
                           lit       = ( frame % 2 != 1 ) )
    self.tab.setTabIcon( led )


  @pyqtSlot()
  def steadyIcon( self ):

    if self.blinker.state() == QTimeLine.Running:
      return

    if not self.world:
      return

    led = self.led.select( connected = self.world.isConnected(),
                           lit       = not self.isVisible() )
    self.tab.setTabIcon( led )


  def windowAlert( self ):

    if not self.world:
      return

    if self.world.conf._alert_on_activity:
      QApplication.instance().alert( self.window() )


  @pyqtSlot()
  def saveSplitterPosition( self ):

    self.world.conf._splitter_sizes = self.sizes()


  def close( self ):

    if self.world.isConnected():

      messagebox = QMessageBox( self.window() )

      messagebox.setWindowTitle( u"Confirm close" )
      messagebox.setIcon( QMessageBox.Question )

      messagebox.setText( u"You are still connected to this world. " \
                          u"Disconnect and close this tab?" )

      messagebox.addButton( u"Close tab", QMessageBox.AcceptRole )
      messagebox.addButton( QMessageBox.Cancel )

      result = messagebox.exec_()

      if result == QMessageBox.Cancel:
        return

    ## The call to ensureWorldDisconnected below is done outside the above
    ## if statement because the world, even if not connected, might be
    ## *trying* to connect, and if so, we want to abort the attempt so that
    ## we don't leak the connection. And ensureWorldDisconnected does just
    ## that.

    self.world.ensureWorldDisconnected()

    ## Then, schedule the closing of the world.
    QTimer.singleShot( 0, self.doClose )


  def doClose( self ):

    self.tab.removeTab()
    self.setParent( None )

    self.world.worldui               = None
    self.world.logger                = None
    self.tab.widget                  = None
    self.output_manager.world        = None
    self.inputui.world               = None
    self.inputui.history.inputwidget = None
    self.actionset.parent            = None

    for f in self.world.socketpipeline.pipeline.filters:
      f.context = None
      f.sink = None

    self.world.socketpipeline.pipeline = None
    self.world.socketpipeline          = None

    self.world = None
    self.deleteLater()


  @pyqtSlot( 'QWidget' )
  def setFocusProxy( self, widget ):

    ## WORKAROUND: PyQt doesn't seem to properly declare the slot for this
    ## method, so we must override it. :/

    QSplitter.setFocusProxy( self, widget )


  def __del__( self ):

    self.world            = None
    self.inputui          = None
    self.secondaryinputui = None
    self.outputui         = None
    self.output_manager   = None
    self.actionset        = None
    self.toolbar          = None
    self.tab              = None
    self.actionset        = None
    self.autocompleter    = None
