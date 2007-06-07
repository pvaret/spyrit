##
## Core.py
##
## Holds the Core class, that does the heavy lifting of everything behind the
## scene (creating worlds, keeping the main window in sync with everything
## that's going on, etc).
##


from localqt import *

class Core( QtCore.QObject ):

  def __init__( s, mw ):

    QtCore.QObject.__init__( s )

    s.mw      = mw
    s.worlds  = []

    from ActionSet import ActionSet
    s.actions = ActionSet()

    s.createActions()


  def createActions( s ):

    s.actions.quit = QtGui.QAction( QtGui.QIcon( ":/icon/quit" ), "Quit", s )
    s.actions.quit.setMenuRole( QtGui.QAction.QuitRole )
    connect( s.actions.quit, SIGNAL( "triggered()" ), s.quit )

    s.actions.aboutqt = QtGui.QAction( "About Qt...", s )
    s.actions.aboutqt.setMenuRole( QtGui.QAction.AboutQtRole )
    connect( s.actions.aboutqt, SIGNAL( "triggered()" ), QtGui.qApp.aboutQt )


  def quit( s ):
    
    for world in s.worlds:
       ## world.disconnect()
       pass

    s.mw.close()
