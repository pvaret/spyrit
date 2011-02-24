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

  def __init__( s ):

    s.CONNECTED_UNLIT    = QIcon( ":/icon/unlit_green_led" )
    s.CONNECTED_LIT      = QIcon( ":/icon/lit_green_led" )
    s.DISCONNECTED_UNLIT = QIcon( ":/icon/unlit_red_led" )
    s.DISCONNECTED_LIT   = QIcon( ":/icon/lit_red_led" )


  def select( s, connected, lit ):

    if connected:
      return lit and s.CONNECTED_LIT or s.CONNECTED_UNLIT

    else:
      return lit and s.DISCONNECTED_LIT or s.DISCONNECTED_UNLIT



class WorldUI( QSplitter ):

  def __init__( s, tabwidget, world ):

    QSplitter.__init__( s, Qt.Vertical, tabwidget )

    assert isinstance( tabwidget, QTabWidget )

    s.world = world
    s.led   = LED()

    s.tab = TabDelegate( s )

    s.tab.tabChanged.connect( s.onTabChanged )

    s.blinker = QTimeLine( 200, s ) ## ms
    s.blinker.setFrameRange( 0, 3 )
    s.blinker.frameChanged.connect( s.iconBlink )
    s.blinker.finished.connect( s.steadyIcon )

    s.world.socketpipeline.addSink( s.startIconBlink,
                                    ChunkData.PACKETBOUND | ChunkData.NETWORK )

    s.alert_timer = SingleShotTimer( s.windowAlert )

    ## Setup input and output UI.

    s.outputui = SplittableTextView( s )
    s.addWidget( s.outputui )

    s.outputui.setFocusProxy( s )

    s.output_manager = OutputManager( world, s.outputui )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )

    s.secondaryinputui = WorldInputUI( s, world, shouldsavehistory=False )
    s.addWidget( s.secondaryinputui )
    s.secondaryinputui.hide()

    s.inputui.returnPressed.connect( s.outputui.pingPage )
    s.secondaryinputui.returnPressed.connect( s.outputui.pingPage )

    s.world.socketpipeline.pipeline.flushBegin.connect(
                              s.output_manager.textcursor.beginEditBlock )

    s.world.socketpipeline.pipeline.flushEnd.connect(
                              s.output_manager.textcursor.endEditBlock )

    s.world.socketpipeline.pipeline.flushEnd.connect( s.outputui.repaint )

    world.socketpipeline.addSink( s.output_manager.processChunk,
                                    ChunkData.TEXT
                                  | ChunkData.FLOWCONTROL
                                  | ChunkData.NETWORK )

    world.socketpipeline.addSink( s.output_manager.textformatmanager.processChunk,
                                    ChunkData.ANSI
                                  | ChunkData.HIGHLIGHT )

    s.setFocusProxy( s.inputui )

    s.inputui.focusChanged.connect( s.setFocusProxy )
    s.secondaryinputui.focusChanged.connect( s.setFocusProxy )

    ## Setup autocompleter.

    s.autocompleter = Autocompleter()
    world.socketpipeline.addSink( s.autocompleter.sink )

    ## Setup splitter.

    s.setChildrenCollapsible( False )
    s.setSizes( world.conf._splitter_sizes )

    s.splitterMoved.connect( s.saveSplitterPosition )

    ## Create toolbar and bind World-related actions.

    s.toolbar = QToolBar()
    s.toolbar.setMovable( False )
    s.toolbar.setFloatable( False )
    s.toolbar.setContextMenuPolicy( Qt.PreventContextMenu )
    s.toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )

    s.toolbar.setWindowTitle( world.title() )

    s.actionset = ActionSet( s )

    s.actionset.bindAction( "stepup",   s.outputui.stepUp )
    s.actionset.bindAction( "stepdown", s.outputui.stepDown )
    s.actionset.bindAction( "pageup",   s.outputui.pageUp )
    s.actionset.bindAction( "pagedown", s.outputui.pageDown )
    s.actionset.bindAction( "home",     s.outputui.moveScrollbarToTop )
    s.actionset.bindAction( "end",      s.outputui.moveScrollbarToBottom )

    s.actionset.bindAction( "toggle2ndinput", s.toggleSecondaryInput )

    connect_action    = s.actionset.bindAction( "connect",
                                              s.world.connectToWorld )

    disconnect_action = s.actionset.bindAction( "disconnect",
                                              s.world.disconnectFromWorld )

    connect_action.setEnabled( False )
    disconnect_action.setEnabled( False )

    startlog_action   = s.actionset.bindAction( "startlog",
                                              s.world.startLogging )

    stoplog_action    = s.actionset.bindAction( "stoplog",
                                              s.world.stopLogging )

    startlog_action.setEnabled( True )
    stoplog_action.setEnabled( False )


    world.disconnected.connect( connect_action.setEnabled )
    world.disconnected.connect( disconnect_action.setDisabled )


    world.nowLogging.connect( startlog_action.setDisabled )
    world.nowLogging.connect( stoplog_action.setEnabled )

    s.toolbar.addAction( connect_action )
    s.toolbar.addAction( disconnect_action )

    s.toolbar.addAction(
      s.actionset.bindAction( "close", s.close )
    )

    s.toolbar.addSeparator()

    s.toolbar.addAction( startlog_action )
    s.toolbar.addAction( stoplog_action )

    s.toolbar.addSeparator()

    s.world.setUI( s )

    for line in QApplication.instance().core.motd:
      s.world.info( line )


  def updateToolBarIcons( s, size ):

    if not size:
      size = QApplication.style().pixelMetric( QStyle.PM_ToolBarIconSize )

    new_size = QSize( size, size )
    s.toolbar.setIconSize( new_size )


  def toggleSecondaryInput( s ):

    if s.secondaryinputui.isHidden():
      s.secondaryinputui.show()
      s.secondaryinputui.setFocus()

    else:
      s.secondaryinputui.hide()
      s.inputui.setFocus()


  @pyqtSlot( bool )
  def onTabChanged( s, is_now_visible ):

    if is_now_visible:

      ## Ensure the currently visible world has focus.
      s.setFocus()
      s.steadyIcon()


  def startIconBlink( s, chunk ):

    ## Don't blink if already blinking:

    if s.blinker.state() != QTimeLine.NotRunning:
      return

    s.blinker.start()
    s.alert_timer.start()


  @pyqtSlot( int )
  def iconBlink( s, frame ):

    if not s.world:
      return

    led = s.led.select( connected = s.world.isConnected(),
                        lit       = ( frame % 2 != 1 ) )
    s.tab.setTabIcon( led )


  @pyqtSlot()
  def steadyIcon( s ):

    if s.blinker.state() == QTimeLine.Running:
      return

    if not s.world:
      return

    led = s.led.select( connected = s.world.isConnected(),
                        lit       = not s.isVisible() )
    s.tab.setTabIcon( led )


  def windowAlert( s ):

    if not s.world:
      return

    if s.world.conf._alert_on_activity:
      QApplication.instance().alert( s.window() )


  #@pyqtSlot()
  def saveSplitterPosition( s ):

    s.world.conf._splitter_sizes = s.sizes()


  def close( s ):

    if s.world.isConnected():

      messagebox = QMessageBox( s.window() )

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

    s.world.ensureWorldDisconnected()

    ## Then, schedule the closing of the world.
    QTimer.singleShot( 0, s.doClose )


  def doClose( s ):

    s.tab.removeTab()
    s.setParent( None )

    s.world.worldui               = None
    s.world.logger                = None
    s.tab.widget                  = None
    s.output_manager.world        = None
    s.inputui.world               = None
    s.inputui.history.inputwidget = None
    s.actionset.parent            = None

    for f in s.world.socketpipeline.pipeline.filters:
      f.context = None
      f.sink = None

    s.world.socketpipeline.pipeline = None
    s.world.socketpipeline          = None

    s.world = None
    s.deleteLater()


  @pyqtSlot( 'QWidget' )
  def setFocusProxy( s, widget ):

    ## WORKAROUND: PyQt doesn't seem to properly declare the slot for this
    ## method, so we must override it. :/

    QSplitter.setFocusProxy( s, widget )


  def __del__( s ):

    s.world            = None
    s.inputui          = None
    s.secondaryinputui = None
    s.outputui         = None
    s.output_manager   = None
    s.actionset        = None
    s.toolbar          = None
    s.tab              = None
    s.actionset        = None
    s.autocompleter    = None
