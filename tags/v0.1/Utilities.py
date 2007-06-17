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


def case_insensitive_cmp( x, y ):

  return ( x.lower() < y.lower() ) and -1 or 1



def handle_exception( exc_type, exc_value, exc_traceback ):

  import sys
  import os.path
  import traceback

  from localqt import QtGui

  ## KeyboardInterrupt is a special case.
  ## We don't raise the error dialog when it occurs.
  if issubclass( exc_type, KeyboardInterrupt ):

    if QtGui.qApp:
      QtGui.qApp.quit()

    return

  filename, line, dummy, dummy = traceback.extract_tb( exc_traceback ).pop()
  filename = os.path.basename( filename )
  error    = "%s: %s" % ( str( exc_type ).split( "'" )[ 1 ].split( "." )[ -1 ],
                          exc_value )

  mw = ( QtGui.qApp and hasattr( QtGui.qApp, "mw" ) and QtGui.qApp.mw ) or None

  QtGui.QMessageBox.critical( mw, "Houston, we have a problem...",
    "<i></i>Whoops. A critical error has occured. This is most likely a bug in "
    + "Spyrit. The error is:<br/>"
    + "<center><b><i>%s</i></b></center><br/>" % error
    + "It occured at <b>line %d</b> of file <b>%s</b>.<br/><br/>"
      % ( line, filename )
    + "Spyrit will now close." )


  print "Spyrit has closed due to an error. This is the full error report:"
  print
  print "".join( traceback.format_exception( exc_type,
                                             exc_value,
                                             exc_traceback ) )
  sys.exit( 1 )
