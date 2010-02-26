# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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


from localqt import *
from PrettyOptionPanel import *

class PrettyOptionDialog( QtGui.QDialog ):

  HEADER_SPACING = 20

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

    if s.panel.layout():

      l, t, r, b = s.panel.layout().getContentsMargins()
      s.panel.layout().setContentsMargins( 0, max( t, s.HEADER_SPACING ), 0, b )

    s.layout().addWidget( s.panel )
    s.layout().addWidget( Separator( s ) )
    s.layout().addWidget( s.buttonbox )
