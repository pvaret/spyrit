# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## CheckVersions.py
##
## This file implements our dependency version checks.
##


REQUIRED_PYTHON_VERSION = ( 3, 6 )
REQUIRED_QT_VERSION     = ( 5, 6 )


def check_python_version():

  import sys
  v = sys.version_info[ 0:2 ]

  if v >= REQUIRED_PYTHON_VERSION:
    return True, "🗸 Found Python v%s.%s." % v

  return False, "Python v%d.%d required!" % REQUIRED_PYTHON_VERSION



def check_pyqt5_installed():

  try:
    import PyQt5
    import PyQt5.QtCore
    return True, "🗸 Found PyQt v%s." % PyQt5.QtCore.PYQT_VERSION_STR

  except ImportError:
    return False, "PyQt5 bindings required!"



def qt_version():

  from PyQt5.QtCore import qVersion

  ## Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).
  return tuple( int( c ) for c in qVersion().split( "." )[ 0:2 ] )



def check_qt_version():

  v = qt_version()

  if v >= REQUIRED_QT_VERSION:
    return True, "🗸 Found Qt v%s.%s." % v[ 0:2 ]

  else:
    return False, "Qt v%d.%d required!" % REQUIRED_QT_VERSION
