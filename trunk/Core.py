##
## Core.py
##
## Holds the Core class, that does the heavy lifting of everything behind the
## scene (creating worlds, keeping the main window in sync with everything
## that's going on, etc).
##


from localqt     import *
from Config      import config, worldconfig
from Utilities   import str_to_int
from AboutDialog import AboutDialog
from Logger      import logger
from World       import World


class Core( QtCore.QObject ):

  def __init__( s, mw ):

    ## We make the QApplication instance this object's parent, so that during
    ## shutdown it doesn't get deleted before the C++ layer has had time to
    ## clean it up.
    QtCore.QObject.__init__( s, QtGui.qApp )

    s.mw      = mw
    s.actions = None

    s.createActions()

    QtCore.QTimer.singleShot( 0, s.afterStart )


  def createActions( s ):

    from ActionSet import ActionSet
    s.actions = ActionSet()

    s.actions.about = \
      QtGui.QAction( QtGui.QIcon( ":/app/icon" ),
                     "About %s..." % config._app_name, s )
    s.actions.about.setMenuRole( QtGui.QAction.AboutRole )
    connect( s.actions.about, SIGNAL( "triggered()" ), AboutDialog.showDialog )

    s.actions.aboutqt = \
      QtGui.QAction( QtGui.QIcon( ":/icon/qt-logo" ), "About Qt...", s )
    s.actions.aboutqt.setMenuRole( QtGui.QAction.AboutQtRole )
    connect( s.actions.aboutqt, SIGNAL( "triggered()" ), QtGui.qApp.aboutQt )

    s.actions.createworld = \
      QtGui.QAction( QtGui.QIcon( ":/icon/new_world" ), "Create world...", s )
    connect( s.actions.createworld,
             SIGNAL( "triggered()" ), s.actionCreateWorld )

    s.actions.quickconnect = QtGui.QAction( "Quick connect...", s )
    connect( s.actions.quickconnect,
             SIGNAL( "triggered()" ), s.actionQuickConnect )

    s.actions.quit = QtGui.QAction( QtGui.QIcon( ":/icon/quit" ), "Quit", s )
    s.actions.quit.setMenuRole( QtGui.QAction.QuitRole )
    s.actions.quit.setShortcut( QtGui.QKeySequence( "Ctrl+Q" ) )
    connect( s.actions.quit, SIGNAL( "triggered()" ), s.quit )


    s.actions.closecurrent = \
      QtGui.QAction( QtGui.QIcon( ":/icon/close" ), "Close", s )
    s.actions.closecurrent.setShortcut( QtGui.QKeySequence( "Ctrl+W" ) )
    connect( s.actions.closecurrent,
             SIGNAL( "triggered()" ), s.actionCloseWorld )




  def knownWorldList( s ):

    return worldconfig.getDomainList()


  def openWorld( s, conf, name=None ):

    world = World( conf, name )
    s.mw.newWorldUI( world )

    world.connectToWorld()
    

  def openWorldByName( s, world ):

    if not worldconfig.hasDomain( world ):
      return

    conf = worldconfig.getDomain( world )
    s.openWorld( conf, world )


  def openWorldByHostPort( s, host, port ):

    conf       = worldconfig.createAnonymousDomain()
    conf._host = host
    conf._port = port
    conf._name = ""

    s.openWorld( conf )



  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    import sys
    from Utilities import handle_exception

    sys.excepthook = handle_exception

    worlds = s.knownWorldList()

    ## At this point, the arguments that Qt uses have already been filtered
    ## by Qt itself.

    for arg in sys.argv[ 1: ]:

      if ":" in arg:  ## This is probably a 'server:port' argument.

        server, port = arg.split( ":", 1 )
        port         = str_to_int( port )  

        if not port or not server:
          logger.warn( "Invalid <server>:<port> command line: %s" % arg )

        else:
          s.openWorldByHostPort( server, port )

      else:

        possiblematches = [ w for w in worlds if w.lower() == arg.lower() ]

        if possiblematches:
          s.openWorldByName( possiblematches[ 0 ] )

        else:
          logger.warn( "No such world: %s" % arg )



  def quit( s ):
    
    s.mw.close()


  def actionCloseWorld( s ):

    worldui = s.mw.currentWorldUI()

    if worldui:
      s.mw.closeWorld( worldui )


  def actionCreateWorld( s ):

    conf       = worldconfig.createAnonymousDomain()
    conf._host = ""
    conf._port = 8000
    conf._name = ""

    from CreateWorldDialog import CreateWorldDialog

    dialog = CreateWorldDialog( conf, s.mw )

    if dialog.exec_():

      name = conf._name
      del conf._name
      conf.saveAsDomain( name )

      s.mw.applyNewConf()

      s.openWorld( conf, name )


  def actionQuickConnect( s ):

    conf       = worldconfig.createAnonymousDomain()
    conf._host = ""
    conf._port = 8000

    from QuickConnectDialog import QuickConnectDialog

    dialog = QuickConnectDialog( conf, s.mw )

    if dialog.exec_():
      s.openWorld( conf )


  def makeConnectToWorldAction( s, world ):

    action = QtGui.QAction( world.replace( "&", "&&" ), s )
    action.setData( QtCore.QVariant( world ) )
    connect( action, SIGNAL( "triggered()" ), s.actionConnectToWorld )

    return action


  def actionConnectToWorld( s ):

    action = s.sender()

    if not action: return

    world = unicode( action.data().toString() )
    s.openWorldByName( world )
