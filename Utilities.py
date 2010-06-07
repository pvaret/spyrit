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
## Utilities.py
##
## This file contains various utility functions.
##


def test_python_version():

  REQUIRED_MAJOR = 2
  REQUIRED_MINOR = 5

  import sys
  v = sys.version_info[ 0:2 ]

  if v >= ( REQUIRED_MAJOR, REQUIRED_MINOR ):
    return True, None

  else:
    return False, u"Python v%d.%d required!" % ( REQUIRED_MAJOR, REQUIRED_MINOR )



def test_pyqt4():

  try:
    import PyQt4
    return True, None

  except ImportError:
    return False, u"PyQt4 bindings required!"



def test_sip_version():

  REQUIRED_MAJOR = 4
  REQUIRED_MINOR = 5

  import sip

  v = tuple( int( c ) for c in sip.SIP_VERSION_STR.split( "." )[:2] )

  if v >= ( REQUIRED_MAJOR, REQUIRED_MINOR ):
    return True, None

  else:
    return False, u"SIP v%d.%d required!" % ( REQUIRED_MAJOR, REQUIRED_MINOR )




def qt_version():

  from PyQt4 import QtCore

  ## Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).
  return tuple( int( c ) for c in QtCore.qVersion().split( "." )[ 0:2 ] )




def test_qt_version():

  REQUIRED_MAJOR = 4
  REQUIRED_MINOR = 4

  v = qt_version()

  if v >= ( REQUIRED_MAJOR, REQUIRED_MINOR ):
    return True, None

  else:
    return False, u"Qt v%d.%d required!" % ( REQUIRED_MAJOR, REQUIRED_MINOR )




def check_ssl_is_available():

  from PyQt4 import QtNetwork
  return hasattr( QtNetwork, "QSslSocket" ) \
         and QtNetwork.QSslSocket.supportsSsl()




def case_insensitive_cmp( x, y ):

  return ( x.lower() < y.lower() ) and -1 or 1



from unicodedata import normalize, category

def make_unicode_translation_table():

  d = {}

  def is_latin_letter( l ):

    return category( l )[ 0 ] == 'L'


  for i in range( 0x1FFF ):

    try:
      c = unichr(i)

    except ValueError:
      continue

    if not is_latin_letter( c ):
      continue

    ## Decompose, then keep only Latin letters in the result.
    cn = normalize( "NFKD", c )
    cn = ''.join( [ l for l in cn if is_latin_letter( l ) ] )

    if cn and cn != c:
      d[ i ] = cn

  return d

UNICODE_TRANSLATION_TABLE = make_unicode_translation_table()


def remove_accents( s ):
  """Turns a Unicode string into its non-accented equivalent.

  >>> print remove_accents( u"Touché!" )
  Touche!

  """

  assert type( s ) is type( u'' )  ## Only accept Unicode strings.

  return s.translate( UNICODE_TRANSLATION_TABLE )


def normalize_text( s ):

  return remove_accents( s ).lower()




def handle_exception( exc_type, exc_value, exc_traceback ):

  import sys
  import os.path
  import traceback

  from localqt import qApp, QtGui

  ## KeyboardInterrupt is a special case.
  ## We don't raise the error dialog when it occurs.
  if issubclass( exc_type, KeyboardInterrupt ):

    if qApp():
      qApp().quit()

    return

  filename, line, dummy, dummy = traceback.extract_tb( exc_traceback ).pop()
  filename = os.path.basename( filename )
  error    = "%s: %s" % ( exc_type.__name__, exc_value )

  from Singletons import singletons

  mw = singletons.mw  ## Will be set to None if no main window yet.

  QtGui.QMessageBox.critical( mw, "Houston, we have a problem...",
    "<center>Whoops. A critical error has occured. This is most likely a bug "
  + "in Spyrit. The error is:<br/><br/>"
  + "<b><i>%s</i></b><br/><br/>" % error
  + "It occured at <b>line %d</b> of file <b>%s</b>.<br/><br/>"
      % ( line, filename )
  + "Spyrit will now close.</center>" )


  print "Spyrit has closed due to an error. This is the full error report:"
  print
  print "".join( traceback.format_exception( exc_type,
                                             exc_value,
                                             exc_traceback ) )
  sys.exit( 1 )
