##
## Utilities.py
##
## This file contains various utility functions.
##


def test_python_version():

  REQUIRED_MAJOR = 2
  REQUIRED_MINOR = 4

  import sys
  v = sys.version_info[ 0:2 ]
  return v >= ( REQUIRED_MAJOR ,REQUIRED_MINOR )


def test_pyqt4():

  try:
    import PyQt4
    return True

  except ImportError:
    return False


def test_qt_version():

  REQUIRED_MAJOR = 4
  REQUIRED_MINOR = 2

  from PyQt4 import QtCore

  ## Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).
  v = tuple( int(c) for c in QtCore.qVersion().split( "." )[ 0:2 ] )

  return v >= ( REQUIRED_MAJOR, REQUIRED_MINOR )


def tuple_to_QPoint( t ):

  try:
    x, y = int( t[0] ), int( t[1] )

  except ( TypeError, IndexError, ValueError ):
    return None

  from localqt import QtCore
  return QtCore.QPoint( x, y )


def tuple_to_QSize( t ):

  try:
    w, h = int( t[0] ), int( t[1] )

  except ( TypeError, IndexError, ValueError ):
    return None

  from localqt import QtCore
  return QtCore.QSize( w, h )
