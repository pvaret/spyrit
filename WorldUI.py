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


class WorldUI( QtGui.QSplitter ):

  def __init__( s, parent, world ):
    
    QtGui.QSplitter.__init__( s, Qt.Vertical, parent )

    s.parent = parent
    s.world  = world
    s.conf   = world.conf

    s.outputui = WorldOutputUI( s, world )
    s.addWidget( s.outputui )
    
    world.socketpipeline.addSink( s.outputui.sink, 
                                [ chunktypes.TEXT,
                                  chunktypes.ENDOFLINE,
                                  chunktypes.NETWORK ] )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )

    s.outputui.setFocusProxy( s.inputui )
    s.setFocusProxy( s.inputui )

    QtCore.QTimer.singleShot( 0, s.inputui, SLOT( "setFocus()" ) )

    s.setChildrenCollapsible( False )
    s.setSizes( s.conf._splitter_sizes )

