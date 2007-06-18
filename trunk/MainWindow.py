##
## MainWindow.py
##
## Holds the MainWindow class, which contains all the core GUI of the program.
##



from localqt import *
from Config  import config
from WorldUI import WorldUI

from Utilities import tuple_to_QSize, tuple_to_QPoint, case_insensitive_cmp


class TabBarWheelEventHandler( QtCore.QObject ):

  def eventFilter( s, tabbar, event ):

    if event.type() == QtCore.QEvent.Wheel \
       and isinstance( tabbar, QtGui.QTabBar ):

      if tabbar.count() <= 1:
        return True

      pos = tabbar.currentIndex()

      if event.delta() < 0:
        pos += 1

      else:
        pos -= 1

      pos = pos % tabbar.count()

      tabbar.setCurrentIndex( pos )

      return True

    else:
      return QtCore.QObject.eventFilter( s, tabbar, event )


class MainWindow( QtGui.QMainWindow ):

  def __init__( s, parent=None ):

    QtGui.QMainWindow.__init__( s, parent )

    ## Create needed members.

    s.maintoolbar = None
    s.connectmenu = QtGui.QMenu()

    ## Set up main window according to its configuration.

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


    ## Load up the core engine, attach it to this window.

    from Core import Core
    s.core = Core( s )

    ## Create the central widget.

    s.tabwidget = QtGui.QTabWidget( s )
    s.setCentralWidget( s.tabwidget )

    s.tabwidget.tabBar().installEventFilter( TabBarWheelEventHandler( s ) )

    connect( s.tabwidget, SIGNAL( "currentChanged ( int )" ), s.ensureTabFocus )
    connect( s.tabwidget, SIGNAL( "currentChanged ( int )" ),
             s.updateActionsState )

    ## Aaand apply the configuration.

    s.refresh()


  def refresh( s ):

    ## Prepare dynamic "Connect to..." menu.

    s.connectmenu.setTitle( "Connect to..." )
    s.connectmenu.setIcon( QtGui.QIcon( ":/icon/connect" ) )
    s.connectmenu.clear()

    worlds = s.core.knownWorldList()

    for world in sorted( worlds, case_insensitive_cmp ):
      s.connectmenu.addAction( s.core.makeConnectToWorldAction( world ) )

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
    filemenu.addAction( s.core.actions.quit )


    worldsmenu = menubar.addMenu( "Worlds" )
    worldsmenu.addAction( s.core.actions.quickconnect )
    worldsmenu.addAction( s.core.actions.createworld )

    worldsmenu.addSeparator()

    if s.connectmenu.isEnabled():
      worldsmenu.addMenu( s.connectmenu )

    else:
      worldsmenu.addAction( s.disabledMenuText( "(No world created)" ) )


    helpmenu = menubar.addMenu( "Help" )
    helpmenu.addAction( s.core.actions.about )
    helpmenu.addAction( s.core.actions.aboutqt )



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

    s.maintoolbar.addAction( s.core.actions.createworld )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( s.core.actions.closecurrent )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( s.core.actions.quit )
    s.maintoolbar.addSeparator()
    s.maintoolbar.addAction( s.core.actions.about )

    s.updateActionsState()
 

  def disabledMenuText( s, text ):

    dummy = QtGui.QAction( text, s )
    dummy.setEnabled( False )

    return dummy


  def iterateOnWorlds( s ):

    for i in range( s.tabwidget.count() ):
      yield s.tabwidget.widget( i )


  def applyNewConf( s ):

    s.setUpdatesEnabled( False )

    s.refresh()

    for world in s.iterateOnWorlds():
      world.refresh()

    s.setUpdatesEnabled( True )

    config.save()


  def updateActionsState( s ):

    worldui = s.currentWorldUI()

    if not worldui:
      s.core.actions.closecurrent.setEnabled( False )

    else:
      s.core.actions.closecurrent.setEnabled( True )


  def newWorldUI( s, world ):

    worldui = WorldUI( s, world )

    pos = s.tabwidget.addTab( worldui, world.displayname )
    s.tabwidget.setCurrentIndex( pos )

    connect( worldui, SIGNAL( "worldWantsToClose( PyQt_PyObject )" ),
             s.closeWorld )

    s.updateActionsState()

    return pos


  def currentWorldUI( s ):

    return s.tabwidget.currentWidget()


  def ensureTabFocus( s, i ):

    s.tabwidget.widget( i ).setFocus()


  def closeWorld( s, worldui ):

    if worldui.world.connected:

      messagebox = QtGui.QMessageBox( s )
      messagebox.setWindowTitle( "Confirm close" )
      messagebox.setText( "You are still connected to this world. "
                        + "Disconnect and close this tab?" )
      messagebox.addButton( "Close tab",   QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( "Cancel", QtGui.QMessageBox.RejectRole )

      messagebox.exec_()

      if messagebox.result() == QtGui.QMessageBox.RejectRole:
        return

      worldui.world.disconnectFromWorld()

    pos = s.tabwidget.indexOf( worldui )
    s.tabwidget.removeTab( pos )

    s.updateActionsState()


  def closeEvent( s, event ):

    ## Confirm close if some worlds are still connected.

    connectedworlds = [ w for w in s.iterateOnWorlds() if w.world.connected ]

    if len( connectedworlds ) > 0:

      messagebox = QtGui.QMessageBox( s )
      messagebox.setWindowTitle( "Confirm quit" )
      messagebox.setText( ( "You are still connected to <b>%s</b> world(s). "
                          + "Close them and quit?" ) % len( connectedworlds ) )
      messagebox.addButton( "Quit",   QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( "Cancel", QtGui.QMessageBox.RejectRole )

      messagebox.exec_()

      if messagebox.result() == QtGui.QMessageBox.RejectRole:

        event.ignore()
        return

    ## Disconnect from current worlds.

    for w in connectedworlds:
      w.world.disconnectFromWorld()

    ## Save the main window's geometry when it's about to be closed.

    size = ( s.size().width(), s.size().height() )
    config._mainwindow_size = size

    pos = ( s.pos().x(), s.pos().y() )
    config._mainwindow_pos = pos

    event.accept()
