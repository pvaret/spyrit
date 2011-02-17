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
## MainWindow.py
##
## Holds the MainWindow class, which contains all the core GUI of the program.
##



from localqt             import *

from WorldUI        import WorldUI
from ActionSet      import ActionSet
from ConfigObserver import ConfigObserver
from SmartTabWidget import SmartTabWidget

from Globals   import CMDCHAR
from Messages  import messages


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, config ):

    QtGui.QMainWindow.__init__( s )

    ## Set up main window according to its configuration.

    s.setWindowTitle( config._app_name )

    min_size = config._mainwindow_min_size
    if min_size and len( min_size ) >= 2:
      s.setMinimumSize( QtCore.QSize( min_size[0], min_size[1] ) )

    size = config._mainwindow_size
    if size and len( size ) >= 2: s.resize( QtCore.QSize( size[0], size[1] ) )

    pos = config._mainwindow_pos
    if pos and len( pos ) >= 2: s.move( QtCore.QPoint( pos[0], pos[1] ) )


    ## Create the central widget.

    default_pane = QtGui.QLabel()
    default_pane.setAlignment( Qt.AlignCenter )
    default_pane.setPixmap( QtGui.QPixmap( ":/app/logo" ) )

    s.setCentralWidget( SmartTabWidget( s, default_pane ) )
    s.tabwidget = s.centralWidget().tabwidget

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
    menubar.setContextMenuPolicy( Qt.PreventContextMenu )

    s.menu_file = menubar.addMenu( u"File" )
    s.menu_file.addAction( s.action_quit )

    s.menu_worlds = menubar.addMenu( u"Worlds" )

    s.menu_connect = QtGui.QMenu()
    s.menu_connect.setTitle( u"Connect to..." )
    s.menu_connect.setIcon( QtGui.QIcon( ":/icon/worlds" ) )

    s.menu_help = menubar.addMenu( u"Help" )
    s.menu_help.addAction( s.action_about )
    s.menu_help.addAction( s.action_aboutqt )


    ## Create toolbars.

    s.toolbar_main = QtGui.QToolBar( u"Main Toolbar", s )
    s.toolbar_main.setMovable( False )
    s.toolbar_main.setFloatable( False )
    s.toolbar_main.setContextMenuPolicy( Qt.PreventContextMenu )
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

    s.initial_style = QtGui.QApplication.style().objectName()

    ## Apply configuration:

    s.refreshStyle()
    s.refreshIcons()

    ## And bind it to the appropriate configuration keys:

    s.observer = ConfigObserver( config )
    s.observer.addCallback( "widget_style", s.refreshStyle )
    s.observer.addCallback( "toolbar_icon_size", s.refreshIcons )

    s.refreshMenuWorlds()

    worldsmanager = qApp().worldsmanager
    connect( worldsmanager, SIGNAL( "worldListChanged()" ),
             s.refreshMenuWorlds )

    ## Set up a MOTD to properly welcome our user:

    MOTD = (
        u"Welcome to %s %s!" % ( config._app_name, config._app_version ),
        u"Type %shelp for help on available commands." % CMDCHAR
    )

    ## Note the use of iter(), so the MOTD is only displayed once for all
    ## worlds.
    s.motd = iter( MOTD )

    ## And with this, our Main Window is created, whee!


  def refreshStyle( s ):

    config = qApp().config
    if not config:
      return

    style = config._widget_style

    if not style: style = s.initial_style

    s.setUpdatesEnabled( False )
    QtGui.QApplication.setStyle( style )
    s.refreshIcons()
    s.setUpdatesEnabled( True )


  def refreshIcons( s ):

    config = qApp().config
    if not config:
      return

    size = config._toolbar_icon_size

    if not size:
      size = QtGui.QApplication.style() \
                  .pixelMetric( QtGui.QStyle.PM_ToolBarIconSize )

    s.toolbar_main.setIconSize( QtCore.QSize( size, size ) )


  def refreshMenuWorlds( s ):

    s.setUpdatesEnabled( False )

    s.menu_worlds.clear()

    s.menu_worlds.addAction( s.action_quickconnect )
    s.menu_worlds.addAction( s.action_newworld )

    s.menu_worlds.addSeparator()

    s.menu_connect.clear()

    worldsmanager = qApp().worldsmanager
    worlds = worldsmanager.knownWorldList()

    if not worlds:

      s.menu_connect.setEnabled( False )
      s.menu_worlds.addAction( s.disabledMenuText( u"(No world created)" ) )

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

    s.setUpdatesEnabled( False )

    worldui = WorldUI( s.tabwidget, world )

    pos = s.tabwidget.addTab( worldui, world.title() )
    s.tabwidget.setCurrentIndex( pos )

    s.setUpdatesEnabled( True )

    return pos


  def closeEvent( s, event ):

    ## Confirm close if some worlds are still connected.

    connectedworlds = [ w for w in s.iterateOnOpenWorlds()
                          if  w.world.isConnected() ]

    if len( connectedworlds ) > 0:

      messagebox = QtGui.QMessageBox( s )

      messagebox.setWindowTitle( u"Confirm quit" )
      messagebox.setIcon( QtGui.QMessageBox.Question )

      messagebox.setText( ( u"You are still connected to <b>%s</b> world(s). "
                            u"Close them and quit?" ) % len( connectedworlds ) )

      messagebox.addButton( u"Quit", QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( QtGui.QMessageBox.Cancel )

      result = messagebox.exec_()

      if result == QtGui.QMessageBox.Cancel:

        event.ignore()
        return

    ## Ensure all the current worlds cut their connections.

    for w in s.iterateOnOpenWorlds():

      if w:
        w.world.ensureWorldDisconnected()
        w.doClose()

    ## Save the main window's geometry when it's about to be closed.

    config = qApp().config

    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    ## WORKAROUND: The version of PyQt that ships in Ubuntu Lucid has a bug
    ## which sometimes causes a segfault when exiting. The following works
    ## around the bug by removing the menu bar from the main window's widget
    ## hierarchy and deleting it ourselves.

    s.hide()
    mb = s.menuBar()
    mb.setParent( None )
    mb.deleteLater()

    ## And we're done, and can quit.
    event.accept()


  def openWorld( s, world ):

    s.newWorldUI( world )
    world.connectToWorld()


  def openWorldByName( s, worldname ):

    worldsmanager = qApp().worldsmanager
    world = worldsmanager.lookupWorldByName( worldname )

    if world:
      s.openWorld( world )

    else:
      messages.warn( u"No such world: %s" % worldname )


  def openWorldByHostPort( s, host, port, ssl=False ):

    worldsmanager = qApp().worldsmanager
    world = worldsmanager.lookupWorldByHostPort( host, port )

    if world:
      s.openWorld( world )

    else:
      s.openWorld(
        worldsmanager.newAnonymousWorld( host, port, ssl )
      )


  def actionNewWorld( s ):

    from NewWorldDialog import NewWorldDialog

    worldsmanager = qApp().worldsmanager
    world  = worldsmanager.newAnonymousWorld()
    dialog = NewWorldDialog( world.conf, s )

    if dialog.exec_():

      world.save()
      s.openWorld( world )


  def actionQuickConnect( s ):

    from QuickConnectDialog import QuickConnectDialog

    worldsmanager = qApp().worldsmanager
    world  = worldsmanager.newAnonymousWorld()
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

    config = qApp().config
    AboutDialog( config, s ).exec_()
