# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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

  ## A few spacing constants used during the layout:

  SPACING = 20
  MARGIN  = 15

  ## The header's stylesheet. The actual colors will be filled in when the
  ## hader is instanciated.

  STYLESHEET = """
    QFrame#header {
      border: 8px inset %s;
      border-image: url(:ui/header_borders) 8px repeat stretch;
    }
  """

  def __init__( s, title, icon=None, desc=None, parent=None ):

    QtGui.QFrame.__init__( s, parent )

    ## The object gets a name so that we can apply the stylesheet to it
    ## specifically.

    s.setObjectName( "header" )

    ## The colors that are used in the stylesheet are retrieved from the
    ## currently configured palette.

    dark = s.palette().dark().color().name()

    s.setStyleSheet( s.STYLESHEET % dark )

    ## Legacy setup for platforms that don't support stylesheets (yet).

    s.setFrameShape(  QtGui.QFrame.StyledPanel )
    s.setFrameShadow( QtGui.QFrame.Plain )

    ## Layout stuff.

    s.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )

    layout = QtGui.QHBoxLayout( s )

    layout.setSpacing( s.SPACING )
    layout.setContentsMargins( s.MARGIN, s.MARGIN, s.MARGIN, s.MARGIN )

    ## And creation of the header's contents.

    if icon:
      i = QtGui.QLabel( s )
      i.setPixmap( icon )
      layout.addWidget( i, 0, Qt.AlignLeft | Qt.AlignVCenter )

    label = '<font size="+2"><b>%s</b></font>' % title
    
    if desc:
      label += '<br><font size="-1"><i>%s</i></font>' % desc

    text = QtGui.QLabel( label, s )
    text.setAlignment( Qt.AlignRight )
    
    text.setTextFormat( Qt.RichText )
    layout.addWidget( text, 0, Qt.AlignRight | Qt.AlignVCenter )

    s.setLayout( layout )
    
