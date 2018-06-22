# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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

from __future__ import absolute_import
from __future__ import unicode_literals

from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QSizePolicy


class PrettyPanelHeader( QFrame ):

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

  def __init__( self, title, icon=None, desc=None, parent=None ):

    QFrame.__init__( self, parent )

    ## The object gets a name so that we can apply the stylesheet to it
    ## specifically.

    self.setObjectName( "header" )

    ## The colors that are used in the stylesheet are retrieved from the
    ## currently configured palette.

    dark = self.palette().dark().color().name()

    self.setStyleSheet( self.STYLESHEET % dark )

    ## Legacy setup for platforms that don't support stylesheets (yet).

    self.setFrameShape(  QFrame.StyledPanel )
    self.setFrameShadow( QFrame.Plain )

    ## Layout stuff.

    self.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )

    layout = QHBoxLayout( self )

    layout.setSpacing( self.SPACING )
    layout.setContentsMargins( self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN )

    ## And creation of the header's contents.

    if icon:
      i = QLabel( self )
      i.setPixmap( icon )
      layout.addWidget( i, 0, Qt.AlignLeft | Qt.AlignVCenter )

    label = '<font size="+2"><b>%s</b></font>' % title

    if desc:
      label += '<br><font size="-1"><i>%s</i></font>' % desc

    text = QLabel( label, self )
    text.setAlignment( Qt.AlignRight )

    text.setTextFormat( Qt.RichText )
    layout.addWidget( text, 0, Qt.AlignRight | Qt.AlignVCenter )

    self.setLayout( layout )

