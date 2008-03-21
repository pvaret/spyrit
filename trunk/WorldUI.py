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
## WorldUI.py
##
## Contains the WorldUI class, which manages a world's widget for reading and
## writing.
##


from localqt import *

from ActionSet      import ActionSet
from TabDelegate    import TabDelegate
from WorldInputUI   import WorldInputUI
from WorldOutputUI  import WorldOutputUI

from Singletons     import singletons
from PipelineChunks import chunktypes



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

  def __init__( s, parent, world ):
    
    QtGui.QSplitter.__init__( s, Qt.Vertical, parent )

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

    s.outputui = WorldOutputUI( s, world )
    s.addWidget( s.outputui )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )
    
    world.socketpipeline.addSink( s.outputui.formatAndDisplay )

    s.setFocusProxy( s.inputui )  ## TODO: correlate this with action of
                                  ## mousewheel on tab bar.

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

    s.actionset.bindAction( "historyup",   s.inputui.historyUp )
    s.actionset.bindAction( "historydown", s.inputui.historyDown )
    s.actionset.bindAction( "pageup",      s.outputui.pageUp )
    s.actionset.bindAction( "pagedown",    s.outputui.pageDown )

    connect_action    = s.actionset.bindAction( "connect",
                                              s.world.connectToWorld )
    disconnect_action = s.actionset.bindAction( "disconnect",
                                              s.world.disconnectFromWorld )

    connect_action.setEnabled( False )
    disconnect_action.setEnabled( False )
    
    connect( world, SIGNAL( "connected( bool )" ),
             connect_action, SLOT( "setDisabled( bool )" ) )

    connect( world, SIGNAL( "connected( bool )" ),
             disconnect_action, SLOT( "setEnabled( bool )" ) )

    s.toolbar.addAction( connect_action )
    s.toolbar.addAction( disconnect_action )

    s.toolbar.addAction(
      s.actionset.bindAction( "close", s.close )
    )

    s.toolbar.addSeparator()

    s.updateToolBarIcons()

    connect( singletons.mw.toolbar_main, SIGNAL( "iconSizeChanged( QSize )" ),
                                         s.updateToolBarIcons )


  def updateToolBarIcons( s, new_size=None ):

    if new_size:
      s.toolbar.setIconSize( new_size )

    else:
      s.toolbar.setIconSize( singletons.mw.toolbar_main.iconSize() )


  def onTabChanged( s, is_now_visible ):

    if is_now_visible:

      ## Ensure the currently visible world has focus.
      s.setFocus()
      s.steadyIcon()


  def startIconBlink( s, chunks ):

    if not s.blinker.state() == QtCore.QTimeLine.Running:
      s.blinker.start()


  def iconBlink( s, frame ):

    led = LED.select( connected = s.world.connected,
                      lit       = ( frame % 2 != 1 ) )
    s.tab.setTabIcon( led )


  def steadyIcon( s ):

    if s.blinker.state() == QtCore.QTimeLine.Running:
      return

    led = LED.select( connected = s.world.connected,
                      lit       = not s.isVisible() )
    s.tab.setTabIcon( led )


  def saveSplitterPosition( s ):

    s.world.conf._splitter_sizes = s.sizes()


  def close( s ):

    if s.world.connected:

      messagebox = QtGui.QMessageBox( singletons.mw )

      messagebox.setWindowTitle( "Confirm close" )
      messagebox.setIcon( QtGui.QMessageBox.Question )

      messagebox.setText( "You are still connected to this world. "
                        + "Disconnect and close this tab?" )

      messagebox.addButton( "Close tab", QtGui.QMessageBox.AcceptRole )
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
    s.tab.removeTab()
    s.cleanupBeforeDelete()


  def cleanupBeforeDelete( s ):

    s.setParent( None )

    s.blinker.stop()

    s.world.cleanupBeforeDelete()
    s.inputui.cleanupBeforeDelete()
    s.outputui.cleanupBeforeDelete()

    s.world     = None
    s.inputui   = None
    s.outputui  = None
    s.actionset = None
    s.toolbar   = None
    s.tab       = None
