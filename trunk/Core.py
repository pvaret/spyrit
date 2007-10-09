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
## Core.py
##
## Holds the Core class, that does the heavy lifting of everything behind the
## scene (creating worlds, keeping the main window in sync with everything
## that's going on, etc).
##


from localqt     import *
from World       import World
from Logger      import logger
from Config      import config, worldconfig
from ActionSet   import ActionSet
from Utilities   import str_to_int
from AboutDialog import AboutDialog



class Core( QtCore.QObject ):

  def __init__( s, mw ):

    ## We make the QApplication instance this object's parent, so that during
    ## shutdown it doesn't get deleted before the C++ layer has had time to
    ## clean it up.
    QtCore.QObject.__init__( s, QtGui.qApp )

    s.mw        = mw
    s.actionset = ActionSet( mw )
    s.actions   = lambda: None  ## This is the simplest object to which you can
                                ## add attributes. :)
    s.createActions()

    QtCore.QTimer.singleShot( 0, s.afterStart )


  def createActions( s ):

    s.actions.about        = s.actionset.bindAction( "about",
                                                      AboutDialog.showDialog ) 
    s.actions.aboutqt      = s.actionset.bindAction( "aboutqt",
                                                      QtGui.qApp.aboutQt )
    s.actions.closecurrent = s.actionset.bindAction( "closecurrent",
                                                      s.actionCloseWorld )
    s.actions.newworld     = s.actionset.bindAction( "newworld",
                                                      s.actionNewWorld )
    s.actions.quickconnect = s.actionset.bindAction( "quickconnect",
                                                      s.actionQuickConnect )
    s.actions.quit         = s.actionset.bindAction( "quit",
                                                      s.quit )
    
    s.actionset.bindAction( "nexttab",     s.mw.tabwidget.tabbar.nextTab )
    s.actionset.bindAction( "previoustab", s.mw.tabwidget.tabbar.previousTab )
    

  def knownWorldList( s ):

    return worldconfig.getDomainList()


  def openWorld( s, conf, name=None ):

    world = World( conf, name )
    s.mw.newWorldUI( world )

    world.connectToWorld()
    

  def openWorldByName( s, world ):

    if not worldconfig.hasDomain( world ):
      return

    conf = worldconfig.getDomain( world )
    s.openWorld( conf, world )


  def openWorldByHostPort( s, host, port ):

    conf = s.newWorldConfig( host, port )
    s.openWorld( conf )


  def afterStart( s ):

    ## This method is called once, right after the start of the event loop.
    ## It is used to set up things that we only want done after the event loop
    ## has begun running.

    import sys
    from Utilities import handle_exception

    sys.excepthook = handle_exception

    worlds = s.knownWorldList()

    ## At this point, the arguments that Qt uses have already been filtered
    ## by Qt itself.

    for arg in sys.argv[ 1: ]:

      if ":" in arg:  ## This is probably a 'server:port' argument.

        server, port = arg.split( ":", 1 )
        port         = str_to_int( port )  

        if not port or not server:
          logger.warn( "Invalid <server>:<port> command line: %s" % arg )

        else:
          s.openWorldByHostPort( server, port )

      else:

        possiblematches = [ w for w in worlds if w.lower() == arg.lower() ]

        if possiblematches:
          s.openWorldByName( possiblematches[0] )

        else:
          logger.warn( "No such world: %s" % arg )



  def quit( s ):
    
    s.mw.close()


  def newWorldConfig( s, host="", port=8000, name="" ):    
    
    conf       = worldconfig.createAnonymousDomain()
    conf._host = host
    conf._port = port
    conf._name = name
    conf._ssl  = False
    
    return conf


  def actionCloseWorld( s ):

    worldui = s.mw.currentWorldUI()

    if worldui:
      s.mw.closeWorld( worldui )


  def actionNewWorld( s ):

    from NewWorldDialog import NewWorldDialog
    
    conf   = s.newWorldConfig()
    dialog = NewWorldDialog( conf, s.mw )

    if dialog.exec_():

      name = conf._name
      del conf._name
      conf.saveAsDomain( name )

      s.mw.applyNewConf()

      s.openWorld( conf, name )


  def actionQuickConnect( s ):
    
    from QuickConnectDialog import QuickConnectDialog
    
    conf   = s.newWorldConfig()
    dialog = QuickConnectDialog( conf, s.mw )

    if dialog.exec_():
      s.openWorld( conf )


  def makeConnectToWorldAction( s, world ):

    action = QtGui.QAction( world.replace( "&", "&&" ), s )
    action.setData( QtCore.QVariant( world ) )
    connect( action, SIGNAL( "triggered()" ), s.actionConnectToWorld )

    return action


  def actionConnectToWorld( s ):

    action = s.sender()

    if not action: return

    world = unicode( action.data().toString() )
    s.openWorldByName( world )
