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
## WorldUI.py
##
## Contains the WorldUI class, which manages a world's widget for reading and
## writing.
##


from localqt import *

from ActionSet          import ActionSet
from TabDelegate        import TabDelegate
from WorldInputUI       import WorldInputUI
from Autocompleter      import Autocompleter
from OutputManager      import OutputManager
from SplittableTextView import SplittableTextView

from Singletons         import singletons
from PipelineChunks     import chunktypes



class LED:

  CONNECTED_UNLIT    = QtGui.QIcon( ":/icon/unlit_green_led" )
  CONNECTED_LIT      = QtGui.QIcon( ":/icon/lit_green_led" )
  DISCONNECTED_UNLIT = QtGui.QIcon( ":/icon/unlit_red_led" )
  DISCONNECTED_LIT   = QtGui.QIcon( ":/icon/lit_red_led" )

  @staticmethod
  def select( connected, lit ):

    if connected:
      return lit and LED.CONNECTED_LIT or LED.CONNECTED_UNLIT

    else:
      return lit and LED.DISCONNECTED_LIT or LED.DISCONNECTED_UNLIT



class WorldUI( QtGui.QSplitter ):

  def __init__( s, tabwidget, world ):
    
    QtGui.QSplitter.__init__( s, Qt.Vertical, tabwidget )

    assert isinstance( tabwidget, QtGui.QTabWidget )

    s.world = world

    s.world.setUI( s )

    s.tab = TabDelegate( s )

    connect( s.tab, SIGNAL( "tabChanged( bool )" ), s.onTabChanged )

    s.blinker = QtCore.QTimeLine( 200 ) ## ms
    s.blinker.setFrameRange( 0, 3 )
    connect( s.blinker, SIGNAL( "frameChanged( int )" ), s.iconBlink )
    connect( s.blinker, SIGNAL( "finished()" ), s.steadyIcon )

    s.world.socketpipeline.addSink( s.startIconBlink )

    ## Setup input and output UI.

    s.outputui = SplittableTextView( s )
    s.addWidget( s.outputui )

    s.output_manager = OutputManager( world, s.outputui )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )

    s.secondaryinputui = WorldInputUI( s, world, shouldsavehistory=False )
    s.addWidget( s.secondaryinputui )
    s.secondaryinputui.hide()
   
    connect( s.inputui,          SIGNAL( "textSent( str )" ),
      s.outputui.pingPage )

    connect( s.secondaryinputui, SIGNAL( "textSent( str )" ),
      s.outputui.pingPage )

    world.socketpipeline.addSink( s.output_manager.formatAndDisplay )

    s.setFocusProxy( s.inputui )

    ## Setup autocompleter.

    s.autocompleter = Autocompleter()
    world.socketpipeline.addSink( s.autocompleter.sink )

    ## Setup splitter.

    s.setChildrenCollapsible( False )
    s.setSizes( world.conf._splitter_sizes )

    connect( s, SIGNAL( "splitterMoved( int, int )" ), s.saveSplitterPosition )

    ## Create toolbar and bind World-related actions.

    s.toolbar = QtGui.QToolBar()
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


    connect( world,          SIGNAL( "disconnected( bool )" ),
             connect_action, SLOT( "setEnabled( bool )" ) )

    connect( world,             SIGNAL( "disconnected( bool )" ),
             disconnect_action, SLOT( "setDisabled( bool )" ) )

    connect( world.logger,    SIGNAL( "nowLogging( bool )" ),
             startlog_action, SLOT( "setDisabled( bool )" ) )

    connect( world.logger,   SIGNAL( "nowLogging( bool )" ),
             stoplog_action, SLOT( "setEnabled( bool )" ) )

    s.toolbar.addAction( connect_action )
    s.toolbar.addAction( disconnect_action )

    s.toolbar.addAction(
      s.actionset.bindAction( "close", s.close )
    )

    s.toolbar.addSeparator()

    s.toolbar.addAction( startlog_action )
    s.toolbar.addAction( stoplog_action )

    s.toolbar.addSeparator()

    s.updateToolBarIcons()

    connect( singletons.mw.toolbar_main, SIGNAL( "iconSizeChanged( QSize )" ),
                                         s.updateToolBarIcons )


  def updateToolBarIcons( s, new_size=None ):

    if new_size:
      s.toolbar.setIconSize( new_size )

    else:
      s.toolbar.setIconSize( singletons.mw.toolbar_main.iconSize() )


  def toggleSecondaryInput( s ):

    if s.secondaryinputui.isHidden():
      s.secondaryinputui.show()
      s.secondaryinputui.setFocus()

    else:
      s.secondaryinputui.hide()
      s.inputui.setFocus()


  def onTabChanged( s, is_now_visible ):

    if is_now_visible:

      ## Ensure the currently visible world has focus.
      s.setFocus()
      s.steadyIcon()


  def startIconBlink( s, chunks ):

    ## Don't blink if already blinking:

    if s.blinker.state() == QtCore.QTimeLine.Running:
      return

    ## Only blink if something interesting is happening:

    types = [ c.chunktype for c in chunks \
              if c.chunktype in ( chunktypes.TEXT,
                                  chunktypes.FLOWCONTROL,
                                  chunktypes.NETWORK ) ]

    if len( types ) == 0:
      return

    s.blinker.start()


  def iconBlink( s, frame ):

    if s.tab and s.world:

      led = LED.select( connected = s.world.isConnected(),
                        lit       = ( frame % 2 != 1 ) )
      s.tab.setTabIcon( led )


  def steadyIcon( s ):

    if s.blinker.state() == QtCore.QTimeLine.Running:
      return

    if s.tab and s.world:

      led = LED.select( connected = s.world.isConnected(),
                        lit       = not s.isVisible() )
      s.tab.setTabIcon( led )


  def saveSplitterPosition( s ):

    s.world.conf._splitter_sizes = s.sizes()


  def close( s ):

    if s.world.isConnected():

      messagebox = QtGui.QMessageBox( singletons.mw )

      messagebox.setWindowTitle( u"Confirm close" )
      messagebox.setIcon( QtGui.QMessageBox.Question )

      messagebox.setText( u"You are still connected to this world. " \
                          u"Disconnect and close this tab?" )

      messagebox.addButton( u"Close tab", QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( QtGui.QMessageBox.Cancel )

      result = messagebox.exec_()

      if result == QtGui.QMessageBox.Cancel:
        return

    ## The call to ensureWorldDisconnected below is done outside the above
    ## if statement because the world, even if not connected, might be
    ## *trying* to connect, and if so, we want to abort the attempt so that
    ## we don't leak the connection. And ensureWorldDisconnected does just
    ## that.

    s.world.ensureWorldDisconnected()

    ## Then, schedule the closing of the world.
    QtCore.QTimer.singleShot( 0, s.doClose )


  def doClose( s ):

    s.tab.removeTab()
    s.setParent( None )

    s.world.worldui               = None
    s.world.logger.world          = None
    s.inputui.commands.commands   = None
    s.inputui.commands.world      = None
    s.inputui.commands            = None
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
