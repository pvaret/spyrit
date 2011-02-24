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
## Application.py
##
## Contains the Application class, which is the QApplication subclass that
## bootstraps the application and gets everything up and running.
##


import sys
import locale

from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import pyqtRemoveInputHook
from PyQt4.QtGui  import QIcon
from PyQt4.QtGui  import QApplication
from PyQt4.QtGui  import QFontDatabase


from Messages   import messages
from Utilities  import handle_exception
from SpyritCore import construct_spyrit_core

## Make it easier to use PDB:
pyqtRemoveInputHook()

class Application( QApplication ):

  def __init__( s, args ):

    QApplication.__init__( s, args )

    s.args           = args
    s.bootstrapped   = False
    s.local_encoding = locale.getpreferredencoding()  ## Try to guess the
                                                      ## local encoding.
    s.core = None

    s.aboutToQuit.connect( s.beforeStop )


  def bootstrap( s ):

    ## Check that we aren't already bootstrapped.
    if s.bootstrapped:
      return

    s.bootstrapped = True

    ## Attempt to load resources. Log error if resources not found.
    try:
      import resources

    except ImportError:
      messages.warn( u"Resource file not found. No graphics will be loaded." )

    ## Load up the dingbat symbols font.
    QFontDatabase.addApplicationFont( ":/app/symbols" )

    ## Setup icon.
    s.setWindowIcon( QIcon( ":/app/icon" ) )

    ## And create the core object for Spyrit:
    s.core = construct_spyrit_core( s )


  def exec_( s ):

    if not s.bootstrapped:
      s.bootstrap()

    QTimer.singleShot( 0, s.afterStart )

    return QApplication.exec_()


  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    sys.excepthook = handle_exception

    s.core.constructMainWindow()

    ## At this point, the arguments that Qt uses have already been filtered
    ## by Qt itself.

    for arg in s.args[ 1: ]:

      arg = arg.decode( s.local_encoding, "replace" )

      if u":" in arg:  ## This is probably a 'server:port' argument.

        server, port = arg.split( u":", 1 )

        try:
          port = int( port )
        except ValueError:
          port = 0

        if not port or not server:
          messages.warn( u"Invalid <server>:<port> command line: %s" % arg )

        else:
          s.core.openWorldByHostPort( server, port )

      else:

        s.core.openWorldByName( arg )


  @pyqtSlot()
  def beforeStop( s ):

    sys.excepthook = sys.__excepthook__
