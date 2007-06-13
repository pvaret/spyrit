##
## Core.py
##
## Holds the Core class, that does the heavy lifting of everything behind the
## scene (creating worlds, keeping the main window in sync with everything
## that's going on, etc).
##


from localqt import *
from Config  import config, worldconfig
from World   import World

class Core( QtCore.QObject ):

  def __init__( s, mw ):

    ## We make the QApplication instance this object's parent, so that during
    ## shutdown it doesn't get deleted before the C++ layer has had time to
    ## clean it up.
    QtCore.QObject.__init__( s, QtGui.qApp )

    s.mw      = mw
    s.worlds  = {}
    s.actions = None

    s.createActions()

    QtCore.QTimer.singleShot( 0, s.afterStart )


  def createActions( s ):

    from ActionSet import ActionSet
    s.actions = ActionSet()

    s.actions.aboutqt = QtGui.QAction( QtGui.QIcon( ":/icon/qt-logo" ),
                                       "About Qt...", s )
    s.actions.aboutqt.setMenuRole( QtGui.QAction.AboutQtRole )
    connect( s.actions.aboutqt, SIGNAL( "triggered()" ), QtGui.qApp.aboutQt )

    s.actions.quickconnect = QtGui.QAction( QtGui.QIcon( ":/icon/connect" ),
                                            "Quick connect...", s)
    connect( s.actions.quickconnect, SIGNAL( "triggered()" ),
                                     s.actionQuickConnect )

    s.actions.quit = QtGui.QAction( QtGui.QIcon( ":/icon/quit" ), "Quit", s )
    s.actions.quit.setMenuRole( QtGui.QAction.QuitRole )
    connect( s.actions.quit, SIGNAL( "triggered()" ), s.quit )


  def knownWorldList( s ):

    return config.getDomain( config._worlds_section ).getDomainList()


  def openWorld( s, conf, name=None ):

    world = World( conf, name )
    pos = s.mw.newWorldUI( world )

    world.connectToWorld()

    s.worlds[ pos ] = world
    

  def openWorldByName( s, world ):

    if not worldconfig.hasDomain( world ):
      return

    conf = worldconfig.getDomain( world )
    s.openWorld( conf, world )

  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    import sys
    from Utilities import handle_exception

    sys.excepthook = handle_exception


  def quit( s ):
    
    for world in s.worlds.itervalues():
       world.disconnectFromWorld()

    s.mw.close()


  def actionQuickConnect( s ):

    conf       = config.createAnonymousDomain()
    conf._host = ""
    conf._port = 8000

    from QuickConnectDialog import QuickConnectDialog

    dialog = QuickConnectDialog( conf, s.mw )

    if dialog.exec_():
      s.openWorld( conf )


  def makeConnectToWorldAction( s, world ):

    action = QtGui.QAction( world, s )
    action.setData( QtCore.QVariant( world ) )
    connect( action, SIGNAL( "triggered()" ), s.actionConnectToWorld )

    return action


  def actionConnectToWorld( s ):

    action = s.sender()

    if not action: return

    world = unicode( action.data().toString() )
    s.openWorldByName( world )
