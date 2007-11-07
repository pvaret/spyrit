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
## MainWindow.py
##
## Holds the MainWindow class, which contains all the core GUI of the program.
##



from localqt             import *

from World               import World
from WorldUI             import WorldUI
from ActionSet           import ActionSet
from Singletons          import singletons
from ScrollableTabWidget import ScrollableTabWidget

from Utilities import tuple_to_QSize, tuple_to_QPoint, case_insensitive_cmp


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    ## Create needed members.

    s.maintoolbar = None
    s.connectmenu = QtGui.QMenu()

    ## Set up main window according to its configuration.

    config = singletons.config

    s.setWindowTitle( config._app_name )

    size = tuple_to_QSize( config._mainwindow_size )
    if size:
      s.resize( size )

    min_size = tuple_to_QSize( config._mainwindow_min_size )
    if min_size: s.setMinimumSize( min_size )

    pos = tuple_to_QPoint( config._mainwindow_pos )
    if pos:
      s.move( pos )

    ## Create the central widget.

    s.tabwidget = ScrollableTabWidget( s )
    s.setCentralWidget( s.tabwidget )

    connect( s.tabwidget, SIGNAL( "currentChanged ( int )" ),
                          s.updateActionsState )

    ## Aaand apply the configuration.

    QtCore.QTimer.singleShot( 0, s.refresh )
    
    
    ## Create all the actions.
    
    s.actionset     = ActionSet( s )
    s.actions       = lambda: None  ## This is the simplest object to which you
                                    ## can add attributes. :)

    s.actions.about        = s.actionset.bindAction( "about",   s.actionAbout ) 
    s.actions.aboutqt      = s.actionset.bindAction( "aboutqt", qApp().aboutQt )
    s.actions.closecurrent = s.actionset.bindAction( "closecurrent",
                                                  s.actionCloseCurrentWorld )
    s.actions.newworld     = s.actionset.bindAction( "newworld",
                                                      s.actionNewWorld )
    s.actions.quickconnect = s.actionset.bindAction( "quickconnect",
                                                      s.actionQuickConnect )
    s.actions.quit         = s.actionset.bindAction( "quit", s.close )
    
    s.actionset.bindAction( "nexttab",     s.tabwidget.tabbar.nextTab )
    s.actionset.bindAction( "previoustab", s.tabwidget.tabbar.previousTab )


  def refresh( s ):

    ## Prepare dynamic "Connect to..." menu.

    s.connectmenu.setTitle( "Connect to..." )
    s.connectmenu.setIcon( QtGui.QIcon( ":/icon/connect" ) )
    s.connectmenu.clear()

    worlds = singletons.worldsmanager.knownWorldList()

    if not worlds:
      s.connectmenu.setEnabled( False )

    else:

      s.connectmenu.setEnabled( True )

      for world in worlds:
        s.connectmenu.addAction( s.makeConnectToWorldAction( world ) )


    ## (Re-)create menus and, if need be, the main toolbar.

    s.createMenus()

    if not s.maintoolbar:
      s.createToolbar()


  def createMenus( s ):

    menubar = s.menuBar()
    menubar.clear()

    filemenu = menubar.addMenu( "File" )
    filemenu.addAction( s.actions.quit )


    worldsmenu = menubar.addMenu( "Worlds" )
    worldsmenu.addAction( s.actions.quickconnect )
    worldsmenu.addAction( s.actions.newworld )

    worldsmenu.addSeparator()

    if s.connectmenu.isEnabled():
      worldsmenu.addMenu( s.connectmenu )

    else:
      worldsmenu.addAction( s.disabledMenuText( "(No world created)" ) )


    helpmenu = menubar.addMenu( "Help" )
    helpmenu.addAction( s.actions.about )
    helpmenu.addAction( s.actions.aboutqt )


  def createToolbar( s ):

    ## Create main toolbar.

    if not s.maintoolbar:

      s.maintoolbar = QtGui.QToolBar( "Main Toolbar", s )
      s.maintoolbar.setMovable( False )
      s.maintoolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )

      s.addToolBar( s.maintoolbar )

    s.maintoolbar.clear()

    ## Create and add dynamic world list action.

    connectaction = s.connectmenu.menuAction()
    s.maintoolbar.addAction( connectaction )

    ## ... And don't forget to set the button for that action to the correct
    ## menu popup mode.

    connectbutton = s.maintoolbar.widgetForAction( connectaction )
    connectbutton.setPopupMode( QtGui.QToolButton.InstantPopup )

    ## Add remaining actions.

    s.maintoolbar.addAction( s.actions.newworld )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( s.actions.closecurrent )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( s.actions.quit )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( s.actions.about )

    s.updateActionsState()
 

  def disabledMenuText( s, text ):

    dummy = QtGui.QAction( text, s )
    dummy.setEnabled( False )

    return dummy


  def iterateOnOpenWorlds( s ):

    for i in range( s.tabwidget.count() ):
      yield s.tabwidget.widget( i )


  def applyNewConf( s ):

    s.setUpdatesEnabled( False )

    s.refresh()

    for world in s.iterateOnOpenWorlds():
      world.refresh()

    s.setUpdatesEnabled( True )

    singletons.config.save()


  def updateActionsState( s ):

    worldui = s.currentWorldUI()

    if not worldui:
      s.actions.closecurrent.setEnabled( False )

    else:
      s.actions.closecurrent.setEnabled( True )


  def newWorldUI( s, world ):

    worldui = WorldUI( s, world )

    pos = s.tabwidget.addTab( worldui, world.displayname )
    s.tabwidget.setCurrentIndex( pos )

    s.updateActionsState()

    return pos


  def currentWorldUI( s ):

    return s.tabwidget.currentWidget()


  def closeWorld( s, worldui ):

    if worldui.world.connected:

      messagebox = QtGui.QMessageBox( s )

      messagebox.setWindowTitle( "Confirm close" )
      messagebox.setIcon( QtGui.QMessageBox.Question )

      messagebox.setText( "You are still connected to this world. "
                        + "Disconnect and close this tab?" )

      messagebox.addButton( "Close tab", QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( QtGui.QMessageBox.Cancel )

      result = messagebox.exec_()

      if result == QtGui.QMessageBox.Cancel:
        return

    ## The call to ensureWorldDisconnected below is done outside the above
    ## if statement because the world, even if not connected, might be
    ## *trying* to connect, and if so, we want to abort the attempt so that
    ## we don't leak the connection. And ensureWorldDisconnected does just
    ## that.

    worldui.world.ensureWorldDisconnected()

    pos = s.tabwidget.indexOf( worldui )
    s.tabwidget.removeTab( pos )

    s.updateActionsState()

    del worldui


  def closeEvent( s, event ):

    ## Confirm close if some worlds are still connected.

    connectedworlds = [ w for w in s.iterateOnOpenWorlds()
                          if  w.world.connected ]

    if len( connectedworlds ) > 0:

      messagebox = QtGui.QMessageBox( s )

      messagebox.setWindowTitle( "Confirm quit" )
      messagebox.setIcon( QtGui.QMessageBox.Question )

      messagebox.setText( ( "You are still connected to <b>%s</b> world(s). "
                          + "Close them and quit?" ) % len( connectedworlds ) )

      messagebox.addButton( "Quit", QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( QtGui.QMessageBox.Cancel )

      result = messagebox.exec_()

      if result == QtGui.QMessageBox.Cancel:

        event.ignore()
        return

    ## Ensure all the current worlds cut their connections.

    for w in s.iterateOnOpenWorlds():
      w.world.ensureWorldDisconnected()

    ## Save the main window's geometry when it's about to be closed.

    config = singletons.config

    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept()


  def openWorld( s, world ):

    s.newWorldUI( world )
    world.connectToWorld()
    

  def openWorldByName( s, worldname ):

    world = singletons.worldsmanager.lookupWorldByName( worldname )

    if world:
      s.openWorld( world )

    else:
      logger.warn( "No such world: %s" % worldname )


  def openWorldByHostPort( s, host, port, ssl=False ):

    world = singletons.worldsmanager.lookupWorldByHostPort( host, port )

    if world:
      s.openWorld( world )

    else:
      s.openWorld( 
        singletons.worldsmanager.newAnonymousWorld( host, port, ssl )
      )


  def actionCloseCurrentWorld( s ):

    worldui = s.currentWorldUI()

    if worldui:
      s.closeWorld( worldui )


  def actionNewWorld( s ):
    ## FIXME: Check why this no longer works!

    from NewWorldDialog import NewWorldDialog
    
    world  = singletons.worldsmanager.newAnonymousWorld()
    dialog = NewWorldDialog( world.conf, s )

    if dialog.exec_():
      name = world.conf._name
      world.conf.saveAsDomain( name )

      s.applyNewConf()

      s.openWorld( world )


  def actionQuickConnect( s ):
    ## FIXME: Check why this no longer works!

    from QuickConnectDialog import QuickConnectDialog
    
    world  = singletons.worldsmanager.newAnonymousWorld()
    dialog = QuickConnectDialog( world.conf, s )

    if dialog.exec_():
      s.openWorld( world )


  def makeConnectToWorldAction( s, worldname ):

    action = QtGui.QAction( worldname.replace( u"&", u"&&" ), s )
    action.setData( QtCore.QVariant( worldname ) )
    connect( action, SIGNAL( "triggered()" ), s.actionConnectToWorld )

    return action


  def actionConnectToWorld( s ):

    action = s.sender()

    if not action: return

    worldname = unicode( action.data().toString() )
    s.openWorldByName( worldname )
    
    
  def actionAbout( s ):
    
    from AboutDialog import AboutDialog
    AboutDialog.showDialog()
