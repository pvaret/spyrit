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
## localqt.py
##
## Imports the PyQt4 functions and namespaces that will be used throughout
## the whole application, for convenience.
##

import sip

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtNetwork

connect    = QtCore.QObject.connect
disconnect = QtCore.QObject.disconnect
emit       = QtCore.QObject.emit
SIGNAL     = QtCore.SIGNAL
SLOT       = QtCore.SLOT

Qt = QtCore.Qt

## Make it easier to use PDB:
QtCore.pyqtRemoveInputHook()

def qApp():

  return QtGui.QApplication.instance()


__all__ = [
  "sip",
  "Qt", "QtCore", "QtGui", "QtNetwork",
  "connect", "disconnect", "emit", "SIGNAL", "SLOT",
  "qApp"
]
