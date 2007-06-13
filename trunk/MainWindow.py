##
## MainWindow.py
##
## Holds the MainWindow class, which contains all the core GUI of the program.
##



from localqt import *
from Config  import config
from WorldUI import WorldUI

from Utilities import tuple_to_QSize, tuple_to_QPoint


class TabBarWheelEventHandler( QtCore.QObject ):

  def eventFilter( s, obj, event ):

    if event.type() == QtCore.QEvent.Wheel \
       and isinstance( obj, QtGui.QTabBar ):

      tabbar = obj

      if tabbar.count() <= 1:
        return True

      pos = tabbar.currentIndex()

      if event.delta() < 0:
        pos += 1

      else:
        pos -= 1

      pos = pos % tabbar.count()

      tabbar.setCurrentIndex( pos )

      return True

    else:
      return QtCore.QObject.eventFilter( s, obj, event )


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    ## Create needed members.
    s.maintoolbar = None

    ## Set up main window according to its configuration.
    s.setWindowTitle( config._app_name )

    size = tuple_to_QSize( config._mainwindow_size )
    if size:
      s.resize( size )

    min_size = tuple_to_QSize( config._mainwindow_min_size )
    if min_size:
      s.setMinimumSize( min_size )

    pos = tuple_to_QPoint( config._mainwindow_pos )
    if pos:
      s.move( pos )


    ## Load up the core engine, attach it to this window.
    from Core import Core
    s.core = Core( s )

    s.createMenus( s.core )
    s.createToolbar( s.core )

    ## And create the central widget. :)
    s.tabwidget = QtGui.QTabWidget( s )
    s.setCentralWidget( s.tabwidget )

    s.tabwidget.tabBar().installEventFilter( TabBarWheelEventHandler( s ) )


  def createMenus( s, core ):

    menubar = s.menuBar()
    menubar.clear()

    filemenu = QtGui.QMenu( "File", menubar )

    filemenu.addAction( core.actions.quit )

    menubar.addMenu( filemenu )

    worldsmenu = QtGui.QMenu( "Worlds", menubar )
    worldsmenu.addAction( core.actions.quickconnect )

    worlds = core.knownWorldList()

    if worlds:

      worldsmenu.addSeparator()
      worldlistmenu = worldsmenu.addMenu( "Connect to" )

      for world in worlds:
        worldlistmenu.addAction( core.makeConnectToWorldAction( world ) )

    menubar.addMenu( worldsmenu )

    helpmenu = QtGui.QMenu( "Help", menubar )

    helpmenu.addAction( core.actions.aboutqt )

    menubar.addMenu( helpmenu )


  def createToolbar( s, core ):

    if not s.maintoolbar:
      s.maintoolbar = QtGui.QToolBar( "Main Toolbar", s )
      s.maintoolbar.setMovable( False )
      s.maintoolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
      s.addToolBar( s.maintoolbar )
    
    s.maintoolbar.addAction( core.actions.quit )
    s.maintoolbar.addAction( core.actions.quickconnect )
    s.maintoolbar.addAction( core.actions.aboutqt )
    


  def newWorldUI( s, world ):

    worldui = WorldUI( s, world )
    pos = s.tabwidget.addTab( worldui, world.displayname )
    s.tabwidget.setCurrentIndex( pos )

    return pos


  def currentWorldUI( s ):

    return s.tabwidget.currentWidget()


  def closeEvent( s, event ):
    
    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept();
