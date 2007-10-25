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

from WorldInputUI   import WorldInputUI
from WorldOutputUI  import WorldOutputUI
from PipelineChunks import chunktypes
from ActionSet      import ActionSet


class WorldUI( QtGui.QSplitter ):

  def __init__( s, parent, world ):
    
    QtGui.QSplitter.__init__( s, Qt.Vertical, parent )

    s.parent = parent
    s.world  = world
    s.conf   = world.conf

    s.world.setUI( s )

    s.outputui = WorldOutputUI( s, world )
    s.addWidget( s.outputui )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )
    
    world.socketpipeline.addSink( s.outputui.formatAndDisplay, 
                                [ chunktypes.TEXT,
                                  chunktypes.ENDOFLINE,
                                  chunktypes.NETWORK,
                                  chunktypes.FORMAT ] )

    s.outputui.setFocusProxy( s.inputui )
    s.setFocusProxy( s.inputui )  ## TODO: correlate this with action of
                                  ## mousewheel on tab bar.

    QtCore.QTimer.singleShot( 0, s.inputui, SLOT( "setFocus()" ) )

    s.setChildrenCollapsible( False )
    s.setSizes( s.conf._splitter_sizes )

    connect( s, SIGNAL( "splitterMoved( int, int )" ), s.saveSplitterPosition )

    s.actionset = ActionSet( s )
    s.createActions()


  def createActions( s ):

    s.actionset.bindAction( "historyup",   s.inputui.historyUp )
    s.actionset.bindAction( "historydown", s.inputui.historyDown )
    s.actionset.bindAction( "pageup",      s.outputui.pageUp )
    s.actionset.bindAction( "pagedown",    s.outputui.pageDown )
    s.actionset.bindAction( "connect",     s.world.connectToWorld )
    s.actionset.bindAction( "disconnect",  s.world.ensureWorldDisconnected )


  def saveSplitterPosition( s ):

    s.conf._splitter_sizes = s.sizes()
