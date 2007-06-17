##
## Separator.py
##
## This file contains the Separator widget, which draws a horizontal line
## and does nothing else.
##


from localqt import *

class Separator( QtGui.QFrame ):

  def __init__( s, parent=None ):

    QtGui.QFrame.__init__( s, parent )

    s.setLineWidth( 1 );
    s.setMidLineWidth( 0 );
    s.setFrameShape ( QtGui.QFrame.HLine )
    s.setFrameShadow( QtGui.QFrame.Sunken )
    s.setMinimumSize( 0, 2 );
