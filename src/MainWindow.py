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

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui  import QIcon
from PyQt4.QtGui  import QMenu
from PyQt4.QtGui  import QLabel
from PyQt4.QtGui  import QStyle
from PyQt4.QtGui  import QAction
from PyQt4.QtGui  import QPixmap
from PyQt4.QtGui  import QToolBar
from PyQt4.QtGui  import QToolButton
from PyQt4.QtGui  import QMainWindow
from PyQt4.QtGui  import QMessageBox
from PyQt4.QtGui  import QApplication

from WorldUI          import WorldUI
from ActionSet        import ActionSet
from SmartTabWidget   import SmartTabWidget
from SettingsObserver import SettingsObserver


class MainWindow( QMainWindow ):

  def __init__( self, settings ):

    QMainWindow.__init__( self )

    ## Set up main window according to its configuration.

    self.setWindowTitle( settings._app._name )

    min_size = settings._ui._window._min_size
    if min_size and min_size.isValid():
      self.setMinimumSize( min_size )

    size = settings._ui._window._size
    if size and size.isValid():
      self.resize( size )

    pos = settings._ui._window._pos
    if pos and not pos.isNull():
      self.move( pos )


    ## Create the central widget.

    default_pane = QLabel()
    default_pane.setAlignment( Qt.AlignCenter )
    default_pane.setPixmap( QPixmap( ":/app/logo" ) )

    self.setCentralWidget( SmartTabWidget( self, default_pane ) )
    self.tabwidget = self.centralWidget().tabwidget

    self.tabwidget.currentChanged.connect( self.setCurrentWorldToolbar )


    ## Create all the actions.

    self.actionset = ActionSet( self )

    self.action_about        = self.actionset.bindAction( "about",   self.actionAbout )
    self.action_aboutqt      = self.actionset.bindAction( "aboutqt", QApplication.instance().aboutQt )
    self.action_newworld     = self.actionset.bindAction( "newworld",
                                                          self.actionNewWorld )
    self.action_quickconnect = self.actionset.bindAction( "quickconnect",
                                                          self.actionQuickConnect )
    self.action_quit         = self.actionset.bindAction( "quit", self.close )

    self.actionset.bindAction( "nexttab",     self.tabwidget.tabbar.nextTab )
    self.actionset.bindAction( "previoustab", self.tabwidget.tabbar.previousTab )


    ## Create menus.

    menubar = self.menuBar()
    menubar.setContextMenuPolicy( Qt.PreventContextMenu )

    self.menu_file = menubar.addMenu( u"File" )
    self.menu_file.addAction( self.action_quit )

    self.menu_worlds = menubar.addMenu( u"Worlds" )

    self.menu_connect = QMenu()
    self.menu_connect.setTitle( u"Connect to..." )
    self.menu_connect.setIcon( QIcon( ":/icon/worlds" ) )

    self.menu_help = menubar.addMenu( u"Help" )
    self.menu_help.addAction( self.action_about )
    self.menu_help.addAction( self.action_aboutqt )


    ## Create toolbars.

    self.toolbar_main = QToolBar( u"Main Toolbar", self )
    self.toolbar_main.setMovable( False )
    self.toolbar_main.setFloatable( False )
    self.toolbar_main.setContextMenuPolicy( Qt.PreventContextMenu )
    self.toolbar_main.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )

    self.addToolBar( self.toolbar_main )

    ## Create and add dynamic world list action.

    connectaction = self.menu_connect.menuAction()
    self.toolbar_main.addAction( connectaction )

    ## ... And don't forget to set the button for that action to the correct
    ## menu popup mode.

    connectbutton = self.toolbar_main.widgetForAction( connectaction )
    connectbutton.setPopupMode( QToolButton.InstantPopup )

    ## Add remaining toolbar actions.

    self.toolbar_main.addAction( self.action_newworld )
    self.toolbar_main.addSeparator()
    self.toolbar_main.addAction( self.action_quit )
    self.toolbar_main.addSeparator()

    self.toolbar_world = None  ## This will be populated when Worlds are created.


    ## Link configuration changes to the appropriate updaters.

    self.initial_style = QApplication.style().objectName()

    ## Apply configuration:

    self.refreshStyle()
    self.refreshIcons()

    ## And bind it to the appropriate configuration keys:

    self.observer = SettingsObserver( settings._ui )
    ##TODO: reactivate
    #self.observer.addCallback( "style", self.refreshStyle )
    #self.observer.addCallback( "toolbar.icon_size", self.refreshIcons )

    self.refreshMenuWorlds()

    worldsmanager = QApplication.instance().core.worlds
    worldsmanager.worldListChanged.connect( self.refreshMenuWorlds )

    ## And with this, our Main Window is created, whee!


  def refreshStyle( self ):

    style = QApplication.instance().core.settings._ui._style

    if not style:
      style = self.initial_style

    self.setUpdatesEnabled( False )
    QApplication.setStyle( style )
    self.refreshIcons()
    self.setUpdatesEnabled( True )


  def refreshIcons( self ):

    size = QApplication.instance().core.settings._ui._toolbar._icon_size

    if not size:
      size = QApplication.style().pixelMetric( QStyle.PM_ToolBarIconSize )

    self.toolbar_main.setIconSize( QSize( size, size ) )


  @pyqtSlot()
  def refreshMenuWorlds( self ):

    self.setUpdatesEnabled( False )

    self.menu_worlds.clear()

    self.menu_worlds.addAction( self.action_quickconnect )
    self.menu_worlds.addAction( self.action_newworld )

    self.menu_worlds.addSeparator()

    self.menu_connect.clear()

    worldsmanager = QApplication.instance().core.worlds
    worlds = worldsmanager.worldList()

    if not worlds:

      self.menu_connect.setEnabled( False )
      self.menu_worlds.addAction( self.disabledMenuText( u"(No world created)" ) )

    else:

      self.menu_connect.setEnabled( True )

      for world in worlds:
        self.menu_connect.addAction( self.makeConnectToWorldAction( world ) )

      self.menu_worlds.addMenu( self.menu_connect )

    self.setUpdatesEnabled( True )


  @pyqtSlot( int )
  def setCurrentWorldToolbar( self, i ):

    self.setUpdatesEnabled( False )

    if self.toolbar_world:
      self.removeToolBar( self.toolbar_world )

    try:
      toolbar = self.tabwidget.widget( i ).toolbar

    except AttributeError:
      toolbar = None

    self.toolbar_world = toolbar

    if toolbar:
      self.addToolBar( toolbar )
      toolbar.show()

    self.setUpdatesEnabled( True )


  def disabledMenuText( self, text ):

    dummy = QAction( text, self )
    dummy.setEnabled( False )

    return dummy


  def iterateOnOpenWorlds( self ):

    for i in range( self.tabwidget.count() ):
      yield self.tabwidget.widget( i )


  def newWorldUI( self, world ):

    self.setUpdatesEnabled( False )

    worldui = WorldUI( self.tabwidget, world )

    pos = self.tabwidget.addTab( worldui, world.title() )
    self.tabwidget.setCurrentIndex( pos )

    self.setUpdatesEnabled( True )

    return pos


  def closeEvent( self, event ):

    ## Confirm close if some worlds are still connected.

    connectedworlds = [ w for w in self.iterateOnOpenWorlds()
                          if  w.world.isConnected() ]

    if len( connectedworlds ) > 0:

      messagebox = QMessageBox( self )

      messagebox.setWindowTitle( u"Confirm quit" )
      messagebox.setIcon( QMessageBox.Question )

      messagebox.setText( ( u"You are still connected to <b>%s</b> world(s). "
                            u"Close them and quit?" ) % len( connectedworlds ) )

      messagebox.addButton( u"Quit", QMessageBox.AcceptRole )
      messagebox.addButton( QMessageBox.Cancel )

      result = messagebox.exec_()

      if result == QMessageBox.Cancel:

        event.ignore()
        return

    ## Ensure all the current worlds cut their connections.

    for w in self.iterateOnOpenWorlds():

      if w:
        w.world.ensureWorldDisconnected()
        w.doClose()

    ## Save the main window's geometry when it's about to be closed.

    settings = QApplication.instance().core.settings

    settings._ui._window._size = self.size()
    settings._ui._window._pos  = self.pos()

    ## WORKAROUND: The version of PyQt that ships in Ubuntu Lucid has a bug
    ## which sometimes causes a segfault when exiting. The following works
    ## around the bug by removing the menu bar from the main window's widget
    ## hierarchy and deleting it ourselves.

    self.hide()
    mb = self.menuBar()
    mb.setParent( None )
    mb.deleteLater()

    ## And we're done, and can quit.
    event.accept()


  def actionNewWorld( self ):

    from NewWorldDialog import NewWorldDialog

    worldsmanager = QApplication.instance().core.worlds
    world  = worldsmanager.newAnonymousWorld()
    dialog = NewWorldDialog( world.settings, self )

    if dialog.exec_():

      world.save()
      QApplication.instance().core.openWorld( world )


  def actionQuickConnect( self ):

    from QuickConnectDialog import QuickConnectDialog

    worldsmanager = QApplication.instance().core.worlds
    world  = worldsmanager.newAnonymousWorld()
    dialog = QuickConnectDialog( world.settings, self )

    if dialog.exec_():
      QApplication.instance().core.openWorld( world )


  def makeConnectToWorldAction( self, worldname ):

    action = QAction( worldname.replace( u"&", u"&&" ), self )
    action.setData( QVariant( worldname ) )
    action.triggered.connect( self.actionConnectToWorld )

    return action


  @pyqtSlot()
  def actionConnectToWorld( self ):

    action = self.sender()

    if not action: return

    worldname = unicode( action.data().toString() )
    QApplication.instance().core.openWorldByName( worldname )


  def actionAbout( self ):

    from AboutDialog import AboutDialog

    settings = QApplication.instance().core.settings
    AboutDialog( settings, self ).exec_()
