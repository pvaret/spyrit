##
## Application.py
##
## Contains the Application class, which is the QApplication subclass that
## bootstraps the application and gets everything up and running.
##



from localqt import *

class Application( QtGui.QApplication ):

  def __init__( s, args=None ):

    if not args:

      import sys
      args = sys.argv

    QtGui.QApplication.__init__( s, args )

    s.bootstrapped = False
    s.config       = None
    s.mw           = None

    connect( s, SIGNAL( "aboutToQuit()" ), s.saveConfig )


  def bootstrap( s ):

    ## Check that we aren't already bootstrapped.
    if s.bootstrapped:
      return

    ## Load the configuration subsystem.
    from Config import config
    s.config = config

    ## Attempt to load resources. Log error if resources not found.
    try:
      import resources

    except ImportError:

      from Logger import logger
      logger.warn( "Resource file not found. No graphics will be loaded." )

    if False: #config._show_splashscreen:

      splash = QtGui.QSplashScreen( QtGui.QPixmap( ":/app/splash" ) )
      splash.show()
      QtGui.qApp.processEvents()

    else: splash = None

    s.setWindowIcon( QtGui.QIcon( ":/app/icon" ) )


    from MainWindow import MainWindow
    s.mw = MainWindow()
    s.mw.show()

    if splash:
      splash.finish( s.mw )

    s.bootstrapped = True


  def exec_( s ):

    if not s.bootstrapped:
      s.bootstrap()

    return QtGui.QApplication.exec_()


  def saveConfig( s ):
    
    if s.config:
      s.config.save()