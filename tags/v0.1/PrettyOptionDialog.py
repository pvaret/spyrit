##
## PrettyOptionDialog.py
##
## This file holds the PrettyOptionDialog class, which makes use of the
## PrettyOptionPanel widget inside a pretty dialog box.
##


from localqt import *
from PrettyOptionPanel import *

class PrettyOptionDialog( QtGui.QDialog ):

  def __init__( s, mapper, header=None, oklabel=None, title=None, parent=None ):

    QtGui.QDialog.__init__( s, parent )

    s.header    = header
    s.panel     = PrettyOptionPanel( mapper )
    s.buttonbox = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok
                                        | QtGui.QDialogButtonBox.Cancel )

    s.okbutton = s.buttonbox.button( QtGui.QDialogButtonBox.Ok )

    if oklabel:
      s.okbutton.setText( oklabel )

    if title:
      s.setWindowTitle( title )

    connect( mapper,     SIGNAL( "isValid( bool )" ),
             s.okbutton, SLOT( "setEnabled( bool )" ) )

    connect( s.buttonbox, SIGNAL( "accepted()" ), s, SLOT( "accept()" ) );
    connect( s.buttonbox, SIGNAL( "rejected()" ), s, SLOT( "reject()" ) );

    mapper.refreshState()

    s.relayout()


  def relayout( s ):

    if s.layout(): 
      sip.delete( s.layout() )

    s.setLayout( QtGui.QVBoxLayout( s ) )

    if s.header:
      s.layout().addWidget( s.header )

    s.layout().addWidget( s.panel )
    s.layout().addWidget( Separator( s ) )
    s.layout().addWidget( s.buttonbox )
