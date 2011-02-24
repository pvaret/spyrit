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

  def __init__( self, mapper, header=None, oklabel=None, title=None, parent=None ):

    QDialog.__init__( self, parent )

    self.header    = header
    self.panel     = PrettyOptionPanel( mapper )
    self.buttonbox = QDialogButtonBox( QDialogButtonBox.Ok
                                     | QDialogButtonBox.Cancel )

    self.okbutton = self.buttonbox.button( QDialogButtonBox.Ok )

    if oklabel:
      self.okbutton.setText( oklabel )

    if title:
      self.setWindowTitle( title )

    mapper.isValid.connect( self.okbutton.setEnabled )

    self.buttonbox.accepted.connect( self.accept )
    self.buttonbox.rejected.connect( self.reject )

    mapper.refreshState()

    self.relayout()


  def relayout( self ):

    if self.layout():
      sip.delete( self.layout() )

    self.setLayout( QVBoxLayout( self ) )

    if self.header:
      self.layout().addWidget( self.header )

    if self.panel.layout():

      l, t, r, b = self.panel.layout().getContentsMargins()
      self.panel.layout().setContentsMargins( 0, max( t, self.HEADER_SPACING ),
                                              0, b )

    self.layout().addWidget( self.panel )
    self.layout().addWidget( Separator( self ) )
    self.layout().addWidget( self.buttonbox )
