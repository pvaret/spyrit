##
## PrettyPanelHeader.py
##
## This file holds the class PrettyPanelHeader, which is a widget that creates
## a pretty header suitable for option panels and such.
##


from localqt import *

class PrettyPanelHeader( QtGui.QFrame ):

  SPACING = 20

  def __init__( s, text, icon=None, parent=None ):

    QtGui.QFrame.__init__( s, parent )

    s.setFrameShape(  QtGui.QFrame.StyledPanel )
    s.setFrameShadow( QtGui.QFrame.Sunken )

    bgcolor = s.palette().color( s.backgroundRole() )
    H, S, V, A = bgcolor.getHsv()
    V = V / 1.1
    newbgcolor = QtGui.QColor.fromHsv( H, S, V, A )

    s.setStyleSheet( "QFrame { background-color: %s }" % newbgcolor.name() )

    s.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )

    layout = QtGui.QHBoxLayout( s )

    layout.setSpacing( s.SPACING )

    if icon:
      i = QtGui.QLabel( s )
      i.setPixmap( icon )
      layout.addWidget( i, 0, Qt.AlignLeft | Qt.AlignVCenter )

    t = QtGui.QLabel( '<font size="+2"><b>%s</b></font>' % text, s )
    t.setTextFormat( Qt.RichText )
    layout.addWidget( t, 0, Qt.AlignRight | Qt.AlignVCenter )

    s.setLayout( layout )
    
