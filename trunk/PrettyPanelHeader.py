# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

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
    s.setFrameShadow( QtGui.QFrame.Plain )

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
    
