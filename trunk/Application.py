# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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

from localqt          import *

from Logger           import logger
from Utilities        import handle_exception, str_to_int


class Application( QtGui.QApplication ):

  def __init__( s, args=None ):

    if not args:
      args = sys.argv

    QtGui.QApplication.__init__( s, args )

    s.bootstrapped = False

    connect( s, SIGNAL( "aboutToQuit()" ), s.saveConfig )


  def bootstrap( s ):

    ## Check that we aren't already bootstrapped.
    if s.bootstrapped:
      return
      
    ## Attempt to load resources. Log error if resources not found.
    try:
      import resources

    except ImportError:
      logger.warn( "Resource file not found. No graphics will be loaded." )

    ## Load and register the singleton classes that are used throughout the
    ## software.

    from Core             import Core
    from Config           import Config
    from MainWindow       import MainWindow
    from WorldsManager    import WorldsManager
    
    from InstanceRegistry import InstanceRegistry

    s.r = InstanceRegistry( 
            ( "mw",            MainWindow ),     ## Main window instance
            ( "core",          Core ),           ## Core engine instance
            ( "config",        Config ),         ## Central configuration object
            ( "worldsmanager", WorldsManager ),  ## Worlds manager instance
          )

    if False: #config._show_splashscreen:

      splash = QtGui.QSplashScreen( QtGui.QPixmap( ":/app/splash" ) )
      splash.show()
      s.processEvents()

    else: splash = None

    s.setWindowIcon( QtGui.QIcon( ":/app/icon" ) )

    s.r.mw.show()

    if splash:
      splash.finish( s.r.mw )

    s.bootstrapped = True


  def exec_( s ):

    if not s.bootstrapped:
      s.bootstrap()

    QtCore.QTimer.singleShot( 0, s.afterStart )
    
    return QtGui.QApplication.exec_()


  def saveConfig( s ):
    
    if s.r.config:
      s.r.config.save()


  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    sys.excepthook = handle_exception

    #worlds = s.knownWorldList() ## TODO: implement

    ## At this point, the arguments that Qt uses have already been filtered
    ## by Qt itself.

    for arg in sys.argv[ 1: ]:

      if ":" in arg:  ## This is probably a 'server:port' argument.

        server, port = arg.split( ":", 1 )
        port         = str_to_int( port )  

        if not port or not server:
          logger.warn( "Invalid <server>:<port> command line: %s" % arg )

        else:
          pass #s.openWorldByHostPort( server, port ) ## TODO: implement

      else:

        possiblematches = [ w for w in worlds if w.lower() == arg.lower() ]

        if possiblematches:
          pass #s.openWorldByName( possiblematches[0] ) ## TODO: implement

        else:
          logger.warn( "No such world: %s" % arg )
