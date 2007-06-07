##
## MainWindow.py
##
## Holds the MainWindow class, which contains all the core GUI of the program.
##



from localqt import *
from Config  import config

from Utilities import tuple_to_QSize, tuple_to_QPoint


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    ## Create needed members.
    s.maintoolbar = None

    ## Set up main window according to its configuration.
    s.setWindowTitle( config._mainwindow_title )

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
    s.createToolbar( s.core)


    ## And create the central widget. :)
#    s.setCentralWidget( QtGui.QTabWidget( s ) )


  def createMenus( s, core ):

    menubar = s.menuBar()

    filemenu = QtGui.QMenu( "File", menubar )

    filemenu.addAction( core.actions.quit )

    menubar.addMenu( filemenu )

    helpmenu = QtGui.QMenu( "Help", menubar )

    helpmenu.addAction( core.actions.aboutqt )

    menubar.addMenu( helpmenu )


  def createToolbar( s, core ):

    if not s.maintoolbar:
      s.maintoolbar = QtGui.QToolBar( "Main Toolbar" )
      s.maintoolbar.setMovable( False )
      s.maintoolbar.setToolButtonStyle( QtCore.Qt.ToolButtonTextUnderIcon )
      s.addToolBar( s.maintoolbar )
    
    s.maintoolbar.addAction( core.actions.quit )
    


  def closeEvent( s, event ):
    
    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept();
