##
## MainWindow.py
##
## Holds the MainWindow class, which contains all the core GUI of the program.
##



from localqt import *
from Config  import config


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    s.setWindowTitle( config._mainwindow_title )

    size = QtCore.QSize()
    size.setWidth( config._mainwindow_size[ 0 ] )
    size.setHeight( config._mainwindow_size[ 1 ] )
    s.resize( size )

    s.setMinimumSize( config._mainwindow_min_width, \
                      config._mainwindow_min_height )

    if config._mainwindow_pos:
      pos = QtCore.QPoint()
      pos.setX( config._mainwindow_pos[ 0 ] )
      pos.setY( config._mainwindow_pos[ 1 ] )
      s.move( pos )

#    s.setCentralWidget( QtGui.QTabWidget( s ) )


  def closeEvent( s, event ):
    
    size = s.size()
    w, h = size.width(), size.height()

    ## We only save the main window's size if it's non-trivial, so as to
    ## avoid user errors.
    if w >= config._mainwindow_min_width \
      and h >= config._mainwindow_min_height:
      config._mainwindow_size = ( size.width(), size.height() )

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept();
