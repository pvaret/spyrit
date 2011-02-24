# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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
## PrettyOptionDialog.py
##
## This file holds the PrettyOptionDialog class, which makes use of the
## PrettyOptionPanel widget inside a pretty dialog box.
##


import sip

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QDialogButtonBox


from Separator         import Separator
from PrettyOptionPanel import PrettyOptionPanel


class PrettyOptionDialog( QDialog ):

  HEADER_SPACING = 20

  def __init__( s, mapper, header=None, oklabel=None, title=None, parent=None ):

    QDialog.__init__( s, parent )

    s.header    = header
    s.panel     = PrettyOptionPanel( mapper )
    s.buttonbox = QDialogButtonBox( QDialogButtonBox.Ok
                                        | QDialogButtonBox.Cancel )

    s.okbutton = s.buttonbox.button( QDialogButtonBox.Ok )

    if oklabel:
      s.okbutton.setText( oklabel )

    if title:
      s.setWindowTitle( title )

    mapper.isValid.connect( s.okbutton.setEnabled )

    s.buttonbox.accepted.connect( s.accept )
    s.buttonbox.rejected.connect( s.reject )

    mapper.refreshState()

    s.relayout()


  def relayout( s ):

    if s.layout():
      sip.delete( s.layout() )

    s.setLayout( QVBoxLayout( s ) )

    if s.header:
      s.layout().addWidget( s.header )

    if s.panel.layout():

      l, t, r, b = s.panel.layout().getContentsMargins()
      s.panel.layout().setContentsMargins( 0, max( t, s.HEADER_SPACING ), 0, b )

    s.layout().addWidget( s.panel )
    s.layout().addWidget( Separator( s ) )
    s.layout().addWidget( s.buttonbox )
