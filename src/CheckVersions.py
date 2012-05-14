# -*- coding: utf-8 -*-

## Copyright (c) 2007-2012 Pascal Varet <p.varet@gmail.com>
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


REQUIRED_PYTHON_VERSION = ( 2, 7 )
REQUIRED_SIP_VERSION    = ( 4, 5 )
REQUIRED_QT_VERSION     = ( 4, 7 )



def check_python_version():

  import sys
  v = sys.version_info[ 0:2 ]

  if v >= REQUIRED_PYTHON_VERSION:
    return True, None

  return False, u"Python v%d.%d required!" % REQUIRED_PYTHON_VERSION



def check_pyqt4_installed():

  try:
    import PyQt4
    return True, None

  except ImportError:
    return False, u"PyQt4 bindings required!"



def check_sip_version():

  try:
    import sip

  except ImportError:
    return False, u"SIP v%d.%d required!" % REQUIRED_SIP_VERSION

  v = tuple( int( c ) for c in sip.SIP_VERSION_STR.split( "." )[:2] )

  if v >= REQUIRED_SIP_VERSION:
    return True, None

  else:
    return False, u"SIP v%d.%d required!" % REQUIRED_SIP_VERSION



def qt_version():

  from PyQt4.QtCore import qVersion

  ## Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).
  return tuple( int( c ) for c in qVersion().split( "." )[ 0:2 ] )



def check_qt_version():

  v = qt_version()

  if v >= REQUIRED_QT_VERSION:
    return True, None

  else:
    return False, u"Qt v%d.%d required!" % REQUIRED_QT_VERSION
