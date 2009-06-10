##
## AboutDialog.py
##
## This is our pretty about dialog! Well, not so pretty yet, but we'll improve
## it later.
##

from localqt import *

from Config            import config
from PrettyPanelHeader import PrettyPanelHeader

ABOUT = """
  <center><br/>
  <b>Spyrit v0.1b</b><br/>
  <br/>
  "Still roughly carved, but coming along nicely."<br/>
  <br/>
  This software is a preliminary development version and does not do much at
  all as of yet. It may not work well for you at all, although I hope it
  will.<br/>
  <br/>
  Watch out for the future versions, which are planned to bring you all the
  nicest features of a good MU* client.<br/>
  </center>
"""

class AboutDialog( QtGui.QDialog ):

  def __init__( s, parent=None ):

    QtGui.QDialog.__init__( s, parent )

    s.setLayout( QtGui.QVBoxLayout( s ) )

    title = "About %s" % config._app_name

    s.setWindowTitle( title )

    header = PrettyPanelHeader( title, QtGui.QPixmap( ":/app/icon" ) )
    s.layout().addWidget( header )

    label = QtGui.QLabel( ABOUT )
    label.setWordWrap( True )
    s.layout().addWidget( label )

    button = QtGui.QPushButton( "Ok" )
    s.layout().addWidget( button )
    s.layout().setAlignment( button, Qt.AlignHCenter )

    connect( button, SIGNAL( "clicked()" ), s, SLOT( "accept()" ) )


  @staticmethod
  def showDialog( parent=None ):

    return AboutDialog( parent ).exec_()
