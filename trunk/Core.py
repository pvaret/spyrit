##
## Core.py
##
## Holds the Core class, that does the heavy lifting of everything behind the
## scene (creating worlds, keeping the main window in sync with everything
## that's going on, etc).
##


from localqt import *
from Config  import config
from World   import World

class Core( QtCore.QObject ):

  def __init__( s, mw ):

    ## We make the QApplication instance this object's parent, so that during
    ## shutdown it doesn't get deleted before the C++ layer has had time to
    ## clean it up.
    QtCore.QObject.__init__( s, QtGui.qApp )

    s.mw      = mw
    s.worlds  = []
    s.actions = None

    s.createActions()

    afterstart = QtCore.QTimer( s )
    afterstart.setSingleShot( True )
    connect( afterstart, SIGNAL( "timeout()" ), s.afterStart )
    afterstart.start( 0 )

    ## Make sure the configuration object has a domain where we can put our
    ## per-world configurations.
    if not config.hasDomain( config._worlds_section ):
      config.createDomain( config._worlds_section )


  def createActions( s ):

    from ActionSet import ActionSet
    s.actions = ActionSet()

    s.actions.quit = QtGui.QAction( QtGui.QIcon( ":/icon/quit" ), "Quit", s )
    s.actions.quit.setMenuRole( QtGui.QAction.QuitRole )
    connect( s.actions.quit, SIGNAL( "triggered()" ), s.quit )

    s.actions.aboutqt = QtGui.QAction( QtGui.QIcon( ":/icon/qt-logo" ),
                                       "About Qt...", s )
    s.actions.aboutqt.setMenuRole( QtGui.QAction.AboutQtRole )
    connect( s.actions.aboutqt, SIGNAL( "triggered()" ), QtGui.qApp.aboutQt )


  def openAnonymousWorld( s, host, port ):

    conf = config.createAnonymousDomain()
    conf._host = host
    conf._port = port

    world   = World( conf )
    s.worlds.append( world )
    s.mw.newWorldUI( world )
    

  def openNamedWorld( s, name ):

    worldsconf = config.getDomain( config._worlds_section )

    if worldsconf.hasDomain( name ):
      world = World( worldsconf.getDomain( name ) )
      s.worlds.append( world )
      s.mw.newWorldUI( world )


  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    import sys
    from Utilities import handle_exception

    sys.excepthook = handle_exception


  def quit( s ):
    
    for world in s.worlds:
       world.disconnectFromWorld()

    s.mw.close()

