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

    s.dummy=QtGui.QWidget()

    s.parent  = parent
    s.world   = world
    s.conf    = world.conf
    s.actions = None

    s.outputui = WorldOutputUI( s, world )
    s.addWidget( s.outputui )
    
    world.socketpipeline.addSink( s.outputui.sink, 
                                [ chunktypes.TEXT,
                                  chunktypes.ENDOFLINE,
                                  chunktypes.NETWORK,
                                  chunktypes.FORMAT ] )

    s.inputui = WorldInputUI( s, world )
    s.addWidget( s.inputui )

    s.outputui.setFocusProxy( s.inputui )
    s.setFocusProxy( s.inputui )

    QtCore.QTimer.singleShot( 0, s.inputui, SLOT( "setFocus()" ) )

    s.setChildrenCollapsible( False )
    s.setSizes( s.conf._splitter_sizes )

    s.createActions()


  def createActions( s ):

    if s.actions:
      return

    s.actions = ActionSet()

    s.actions.historyup = \
        QtGui.QAction( QtGui.QIcon( ":/icon/up" ), "History Up", s.inputui )
    s.actions.historyup.setShortcut( QtGui.QKeySequence( "Alt+Up" ) )
    s.actions.historyup.setShortcutContext( Qt.WidgetShortcut )
    connect( s.actions.historyup, SIGNAL( "triggered()" ), s.inputui.historyUp )

    s.inputui.addAction( s.actions.historyup )

    s.actions.historydown = \
        QtGui.QAction( QtGui.QIcon( ":/icon/down" ), "History Down", s.inputui )
    s.actions.historydown.setShortcut( QtGui.QKeySequence( "Alt+Down" ) )
    s.actions.historydown.setShortcutContext( Qt.WidgetShortcut )
    connect( s.actions.historydown,
             SIGNAL( "triggered()" ), s.inputui.historyDown )

    s.inputui.addAction( s.actions.historydown )
