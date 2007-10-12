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

from WorldUI             import WorldUI
from ScrollableTabWidget import ScrollableTabWidget

from Utilities import tuple_to_QSize, tuple_to_QPoint, case_insensitive_cmp


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    ## Create needed members.

    s.maintoolbar = None
    s.connectmenu = QtGui.QMenu()

    ## Set up main window according to its configuration.

    config = qApp().r.config

    s.setWindowTitle( config._app_name )

    size = tuple_to_QSize( config._mainwindow_size )
    if size:
      s.resize( size )

    min_size = tuple_to_QSize( config._mainwindow_min_size )
    if min_size:
      s.setMinimumSize( min_size )

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


  def refresh( s ):

    ## Prepare dynamic "Connect to..." menu.

    s.connectmenu.setTitle( "Connect to..." )
    s.connectmenu.setIcon( QtGui.QIcon( ":/icon/connect" ) )
    s.connectmenu.clear()

    worlds = qApp().r.worldsmanager.knownWorldList()

    for world in sorted( worlds, case_insensitive_cmp ):
      s.connectmenu.addAction( qApp().r.core.makeConnectToWorldAction( world ) )

    if len( worlds ) == 0:
      s.connectmenu.setEnabled( False )

    else:
      s.connectmenu.setEnabled( True )

    ## (Re-)create menus and, if need be, the main toolbar.

    s.createMenus()

    if not s.maintoolbar:
      s.createToolbar()


  def createMenus( s ):

    menubar = s.menuBar()
    menubar.clear()


    filemenu = menubar.addMenu( "File" )
    filemenu.addAction( qApp().r.core.actions.quit )


    worldsmenu = menubar.addMenu( "Worlds" )
    worldsmenu.addAction( qApp().r.core.actions.quickconnect )
    worldsmenu.addAction( qApp().r.core.actions.newworld )

    worldsmenu.addSeparator()

    if s.connectmenu.isEnabled():
      worldsmenu.addMenu( s.connectmenu )

    else:
      worldsmenu.addAction( s.disabledMenuText( "(No world created)" ) )


    helpmenu = menubar.addMenu( "Help" )
    helpmenu.addAction( qApp().r.core.actions.about )
    helpmenu.addAction( qApp().r.core.actions.aboutqt )



  def createToolbar( s):

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

    s.maintoolbar.addAction( qApp().r.core.actions.newworld )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( qApp().r.core.actions.closecurrent )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( qApp().r.core.actions.quit )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( qApp().r.core.actions.about )

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

    qApp().r.config.save()


  def updateActionsState( s ):

    worldui = s.currentWorldUI()

    if not worldui:
      qApp().r.core.actions.closecurrent.setEnabled( False )

    else:
      qApp().r.core.actions.closecurrent.setEnabled( True )


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

    config = qApp().r.config

    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept()
