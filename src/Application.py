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

from localqt     import *

from Messages    import messages
from Utilities   import handle_exception
from ConfigPaths import CONFIG_FILE

from Config          import Config
from TriggersManager import TriggersManager
from WorldsManager   import WorldsManager
from MainWindow      import MainWindow

from TempResources   import TempResources
from SoundEngine     import SoundEngine
from CommandRegistry import CommandRegistry, register_local_commands


class Application( QtGui.QApplication ):

  def __init__( s, args ):

    QtGui.QApplication.__init__( s, args )

    s.args           = args
    s.bootstrapped   = False
    s.local_encoding = locale.getpreferredencoding()  ## Try to guess the
                                                      ## local encoding.
    s.mw              = None
    s.tmprc           = None
    s.sound           = None
    s.config          = None
    s.commands        = None
    s.worldsmanager   = None
    s.triggersmanager = None


    connect( s, SIGNAL( "aboutToQuit()" ), s.beforeStop )


  def bootstrap( s ):

    ## Check that we aren't already bootstrapped.
    if s.bootstrapped:
      return

    ## Attempt to load resources. Log error if resources not found.
    try:
      import resources

    except ImportError:
      messages.warn( u"Resource file not found. No graphics will be loaded." )

    ## Load up the dingbat symbols font.
    QtGui.QFontDatabase.addApplicationFont( ":/app/symbols" )

    ## Setup icon.
    s.setWindowIcon( QtGui.QIcon( ":/app/icon" ) )

    ## Load and register the singleton instances that are used throughout
    ## the software. Note that they are created in the order they depend
    ## on each other.

    s.config          = Config()
    s.triggersmanager = TriggersManager( s.config )
    s.worldsmanager   = WorldsManager( s.config )
    s.mw              = MainWindow( s.config )

    s.mw.show()

    ## Load up additional global resources.

    s.tmprc    = TempResources()
    s.sound    = SoundEngine()
    s.commands = CommandRegistry()

    ## The command registry has to be populated with what commands have
    ## been implemented at this point. The register_local_commands function
    ## knows how to do that.

    register_local_commands( s.commands )

    s.bootstrapped = True


  def exec_( s ):

    if not s.bootstrapped:
      s.bootstrap()

    QtCore.QTimer.singleShot( 0, s.afterStart )

    return QtGui.QApplication.exec_()


  def saveConfig( s ):

    if s.config:
      s.config.save( CONFIG_FILE )


  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    sys.excepthook = handle_exception

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
          s.mw.openWorldByHostPort( server, port )

      else:

        s.mw.openWorldByName( arg )


  def beforeStop( s ):

    s.saveConfig()
    sys.excepthook = sys.__excepthook__
