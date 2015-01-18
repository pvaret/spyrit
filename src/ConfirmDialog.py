# -*- coding: utf-8 -*-

## Copyright (c) 2007-2015 Pascal Varet <p.varet@gmail.com>
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
## ConfirmDialog.py
##
## Provides a simpler confirmation dialog wrapper function.
##


from PyQt4.QtGui  import QMessageBox


def confirmDialog( title, msg, okbutton, widget=None ):

  messagebox = QMessageBox( widget )

  messagebox.setIcon( QMessageBox.Question )
  messagebox.setWindowTitle( title )
  messagebox.setText( msg )

  messagebox.addButton( okbutton, QMessageBox.AcceptRole )
  messagebox.addButton( QMessageBox.Cancel )

  return ( messagebox.exec_() != QMessageBox.Cancel )
