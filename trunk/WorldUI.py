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
from WorldInputUI   import WorldInputUI
from WorldOutputUI  import WorldOutputUI
from PipelineChunks import chunktypes


class WorldUI( QtGui.QSplitter ):

  def __init__( s, parent, world ):
    
    QtGui.QSplitter.__init__( s, Qt.Vertical, parent )

    s.world = world

    s.world.setUI( s )

    s.outputui = WorldOutputUI( s, world )
    s.addWidget( s.outputui )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )
    
    world.socketpipeline.addSink( s.outputui.formatAndDisplay )

    s.outputui.setFocusProxy( s.inputui )
    s.setFocusProxy( s.inputui )  ## TODO: correlate this with action of
                                  ## mousewheel on tab bar.

    QtCore.QTimer.singleShot( 0, s.inputui, SLOT( "setFocus()" ) )

    s.setChildrenCollapsible( False )
    s.setSizes( world.conf._splitter_sizes )

    connect( s, SIGNAL( "splitterMoved( int, int )" ), s.saveSplitterPosition )

    ## Create toolbar and bind World-related actions.

    s.toolbar = QtGui.QToolBar()
    s.toolbar.setMovable( False )
    s.toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )

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
      s.actionset.bindAction( "close", s.world.close )
    )

    s.toolbar.addSeparator()


  def saveSplitterPosition( s ):

    s.world.conf._splitter_sizes = s.sizes()


  def cleanupBeforeDelete( s ):

    s.setParent( None )

    s.world.cleanupBeforeDelete()
    s.inputui.cleanupBeforeDelete()
    s.outputui.cleanupBeforeDelete()

    del s.world
    del s.inputui
    del s.outputui
    del s.actionset
    del s.toolbar
