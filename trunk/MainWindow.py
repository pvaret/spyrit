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

#    s.setCentralWidget( QtGui.QTabWidget( s ) )


  def closeEvent( s, event ):
    
    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept();
