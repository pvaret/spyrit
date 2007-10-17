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


from localqt    import *

from World      import World
from ActionSet  import ActionSet
from Singletons import singletons



class Core( QtCore.QObject ):

  def __init__( s ):

    ## We make the QApplication instance this object's parent, so that during
    ## shutdown it doesn't get deleted before the C++ layer has had time to
    ## clean it up.
    QtCore.QObject.__init__( s, qApp() )

    s.mw            = singletons.mw
    s.actionset     = ActionSet( s.mw )
    s.actions       = lambda: None  ## This is the simplest object to which you
                                    ## can add attributes. :)
    s.createActions()


  def createActions( s ):

    from AboutDialog import AboutDialog

    s.actions.about        = s.actionset.bindAction( "about",
                                                      AboutDialog.showDialog ) 
    s.actions.aboutqt      = s.actionset.bindAction( "aboutqt",
                                                      qApp().aboutQt )
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
    

  def openWorld( s, conf, name=None ):

    world = World( conf, name )
    s.mw.newWorldUI( world )

    world.connectToWorld()
    

  def openWorldByName( s, worldname ):

    worldconfig = singletons.worldsmanager.worldconfig

    if not worldconfig.hasDomain( worldname ):
      return

    conf = worldconfig.getDomain( worldname )
    s.openWorld( conf, worldname )


  def openWorldByHostPort( s, host, port ):

    conf = s.newWorldConfig( host, port )
    s.openWorld( conf )


  def quit( s ):
    
    s.mw.close()


  def newWorldConfig( s, host="", port=8000, name="" ):    

    worldconfig = singletons.worldsmanager.worldconfig

    worldconf       = worldconfig.createAnonymousDomain()
    worldconf._host = host
    worldconf._port = port
    worldconf._name = name
    worldconf._ssl  = False
    
    return worldconf


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


  def makeConnectToWorldAction( s, worldname ):

    action = QtGui.QAction( worldname.replace( "&", "&&" ), s )
    action.setData( QtCore.QVariant( worldname ) )
    connect( action, SIGNAL( "triggered()" ), s.actionConnectToWorld )

    return action


  def actionConnectToWorld( s ):

    action = s.sender()

    if not action: return

    worldname = unicode( action.data().toString() )
    s.openWorldByName( worldname )
