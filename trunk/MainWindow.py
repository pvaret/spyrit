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
from ConfigObserver      import ConfigObserver
from ScrollableTabWidget import ScrollableTabWidget

from Messages  import messages
from Utilities import tuple_to_QSize, tuple_to_QPoint, case_insensitive_cmp


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    ## Set up main window according to its configuration.

    config = singletons.config

    s.setWindowTitle( config._app_name )

    size = tuple_to_QSize( config._mainwindow_size )
    if size: s.resize( size )

    min_size = tuple_to_QSize( config._mainwindow_min_size )
    if min_size: s.setMinimumSize( min_size )

    pos = tuple_to_QPoint( config._mainwindow_pos )
    if pos: s.move( pos )


    ## Create the central widget.

    s.tabwidget = ScrollableTabWidget( s )
    s.setCentralWidget( s.tabwidget )

    connect( s.tabwidget, SIGNAL( "currentChanged ( int )" ),
                          s.setCurrentWorldToolbar )

    
    ## Create all the actions.
    
    s.actionset = ActionSet( s )

    s.action_about        = s.actionset.bindAction( "about",   s.actionAbout ) 
    s.action_aboutqt      = s.actionset.bindAction( "aboutqt", qApp().aboutQt )
    s.action_newworld     = s.actionset.bindAction( "newworld",
                                                     s.actionNewWorld )
    s.action_quickconnect = s.actionset.bindAction( "quickconnect",
                                                     s.actionQuickConnect )
    s.action_quit         = s.actionset.bindAction( "quit", s.close )
    
    s.actionset.bindAction( "nexttab",     s.tabwidget.tabbar.nextTab )
    s.actionset.bindAction( "previoustab", s.tabwidget.tabbar.previousTab )


    ## Create menus.

    menubar = s.menuBar()

    s.menu_file = menubar.addMenu( "File" )
    s.menu_file.addAction( s.action_quit )

    s.menu_worlds = menubar.addMenu( "Worlds" )

    s.menu_connect = QtGui.QMenu()
    s.menu_connect.setTitle( "Connect to..." )
    s.menu_connect.setIcon( QtGui.QIcon( ":/icon/worlds" ) )

    s.refreshMenuWorlds()

    s.menu_help = menubar.addMenu( "Help" )
    s.menu_help.addAction( s.action_about )
    s.menu_help.addAction( s.action_aboutqt )


    ## Create toolbars.

    s.toolbar_main = QtGui.QToolBar( "Main Toolbar", s )
    s.toolbar_main.setMovable( False )
    s.toolbar_main.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )

    s.addToolBar( s.toolbar_main )

    ## Create and add dynamic world list action.

    connectaction = s.menu_connect.menuAction()
    s.toolbar_main.addAction( connectaction )

    ## ... And don't forget to set the button for that action to the correct
    ## menu popup mode.

    connectbutton = s.toolbar_main.widgetForAction( connectaction )
    connectbutton.setPopupMode( QtGui.QToolButton.InstantPopup )

    ## Add remaining toolbar actions.

    s.toolbar_main.addAction( s.action_newworld )
    s.toolbar_main.addSeparator()
    s.toolbar_main.addAction( s.action_quit )
    s.toolbar_main.addSeparator()
 
    s.toolbar_world = None  ## This will be populated when Worlds are created.


    ## Link configuration changes to the appropriate updaters.

    ConfigObserver( config.getDomain( config._worlds_section ) ) \
                   .addCallback( config.SECTIONS, s.refreshMenuWorlds )

    ## And with this, our Main Window is created, whee!


  def refreshMenuWorlds( s ):

    s.setUpdatesEnabled( False )

    s.menu_worlds.clear()

    s.menu_worlds.addAction( s.action_quickconnect )
    s.menu_worlds.addAction( s.action_newworld )

    s.menu_worlds.addSeparator()

    s.menu_connect.clear()

    worlds = singletons.worldsmanager.knownWorldList()

    if not worlds:

      s.menu_connect.setEnabled( False )
      s.menu_worlds.addAction( s.disabledMenuText( "(No world created)" ) )

    else:

      s.menu_connect.setEnabled( True )

      for world in worlds:
        s.menu_connect.addAction( s.makeConnectToWorldAction( world ) )

      s.menu_worlds.addMenu( s.menu_connect )

    s.setUpdatesEnabled( True )


  def setCurrentWorldToolbar( s, i ):

    s.setUpdatesEnabled( False )

    if s.toolbar_world:
      s.removeToolBar( s.toolbar_world )

    try:
      toolbar = s.tabwidget.widget( i ).toolbar

    except AttributeError:
      toolbar = None

    s.toolbar_world = toolbar

    if toolbar:
      s.addToolBar( toolbar )
      toolbar.show()

    s.setUpdatesEnabled( True )


  def disabledMenuText( s, text ):

    dummy = QtGui.QAction( text, s )
    dummy.setEnabled( False )

    return dummy


  def iterateOnOpenWorlds( s ):

    for i in range( s.tabwidget.count() ):
      yield s.tabwidget.widget( i )


  def newWorldUI( s, world ):

    worldui = WorldUI( s, world )

    pos = s.tabwidget.addTab( worldui, world.title() )
    s.tabwidget.setCurrentIndex( pos )

    return pos


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
        return False

    ## The call to ensureWorldDisconnected below is done outside the above
    ## if statement because the world, even if not connected, might be
    ## *trying* to connect, and if so, we want to abort the attempt so that
    ## we don't leak the connection. And ensureWorldDisconnected does just
    ## that.

    worldui.world.ensureWorldDisconnected()

    pos = s.tabwidget.indexOf( worldui )
    s.tabwidget.removeTab( pos )

    worldui.cleanupBeforeDelete()

    return True


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
      messages.warn( "No such world: %s" % worldname )


  def openWorldByHostPort( s, host, port, ssl=False ):

    world = singletons.worldsmanager.lookupWorldByHostPort( host, port )

    if world:
      s.openWorld( world )

    else:
      s.openWorld( 
        singletons.worldsmanager.newAnonymousWorld( host, port, ssl )
      )


  def actionNewWorld( s ):

    from NewWorldDialog import NewWorldDialog
    
    world  = singletons.worldsmanager.newAnonymousWorld()
    dialog = NewWorldDialog( world.conf, s )

    if dialog.exec_():

      world.save()
      s.openWorld( world )

    else:
      world.cleanupBeforeDelete()


  def actionQuickConnect( s ):

    from QuickConnectDialog import QuickConnectDialog
    
    world  = singletons.worldsmanager.newAnonymousWorld()
    dialog = QuickConnectDialog( world.conf, s )

    if dialog.exec_():
      s.openWorld( world )

    else:
      world.cleanupBeforeDelete()


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
