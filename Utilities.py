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

u"""
:doctest:

>>> from Utilities import *

"""


REQUIRED_PYTHON_VERSION = ( 2, 5 )
REQUIRED_SIP_VERSION    = ( 4, 5 )
REQUIRED_QT_VERSION     = ( 4, 5 )



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

  import sip

  v = tuple( int( c ) for c in sip.SIP_VERSION_STR.split( "." )[:2] )

  if v >= REQUIRED_SIP_VERSION:
    return True, None

  else:
    return False, u"SIP v%d.%d required!" % REQUIRED_SIP_VERSION




def qt_version():

  from PyQt4 import QtCore

  ## Parse qVersion (of the form "X.Y.Z") into a tuple of (major, minor).
  return tuple( int( c ) for c in QtCore.qVersion().split( "." )[ 0:2 ] )




def check_qt_version():

  v = qt_version()

  if v >= REQUIRED_QT_VERSION:
    return True, None

  else:
    return False, u"Qt v%d.%d required!" % REQUIRED_QT_VERSION




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
      c = unichr( i )

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

def remove_accents( string, translation_table=UNICODE_TRANSLATION_TABLE ):
  u"""\
  Filters the diacritics off Latin characters in the given Unicode string.

  >>> print remove_accents( u"Touché!" )
  Touche!

  """

  assert type( string ) is type( u'' )  ## Only accept Unicode strings.

  return string.translate( translation_table )


def normalize_text( string ):

  return remove_accents( string ).lower()


def ensure_valid_filename( filename ):

  u"""\
  Make the given string safe(r) to use as a filename.

  Some platforms refuse certain characters in filenames. This function filters
  those characters out of the given string and replaces them with an
  underscore.

  The resulting string is not guaranteed to be valid, because ultimately it's
  the filesystem's call and we can't second-guess it. This function only makes
  a best-effort attempt which should hopefully suffice in most cases.

  Note: the filename must be given as Unicode.

  >>> print ensure_valid_filename( u'(127.0.0.1:*).log' )
  (127.0.0.1__).log

  """

  assert type( filename ) is type( u'' )  ## Only accept Unicode strings.

  invalid_char_codes = range( 32 )
  invalid_char_codes.extend( ord( c ) for c in u'<>:"/\\|?*' )

  translation_table = dict( ( c, u'_' ) for c in invalid_char_codes )

  return filename.translate( translation_table )


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


def format_as_table( columns, headers ):
  u"""\
  Format a set of columns and headers as a table.

  >>> print format_as_table( columns=( [ 'item 1' ], [ 'item 2' ] ),
  ...                        headers=[ 'Header A', 'Header B' ] )
  Header A    Header B
  --------    --------
  item 1      item 2

  """

  if len( headers ) < len( columns ):
    headers = list( headers ) + [ '' ] * ( len( columns ) - len( headers ) )

  for column, header in zip( columns, headers ):

    column.insert( 0, header )
    column.insert( 1, "-" * len( header ) )

    justify_to = max( len( item ) for item in column )

    for i, item in enumerate( column ):
      column[ i ] = item.ljust( justify_to + 4 )

  return '\n'.join( ''.join( line ).rstrip() for line in zip( *columns ) )
