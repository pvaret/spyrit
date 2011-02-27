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
## World.py
##
## Holds the class that manages the state of a world: input, output, connection
## and disconnection, etc.
##


import os
import time

from glob import glob

from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui  import QFileDialog
from PyQt4.QtGui  import QMessageBox
from PyQt4.QtGui  import QApplication


from ConfigObserver   import ConfigObserver
from PlatformSpecific import platformSpecific
from Utilities        import ensure_valid_filename
from Logger           import create_logger_for_world
from Globals          import CMDCHAR
from SingleShotTimer  import SingleShotTimer

from pipeline                import ChunkData
from pipeline.SocketPipeline import SocketPipeline




class Status:

  DISCONNECTED  = 0
  CONNECTING    = 1
  CONNECTED     = 2
  DISCONNECTING = 3


class World( QObject ):

  connected    = pyqtSignal( bool )
  disconnected = pyqtSignal( bool )
  nowLogging   = pyqtSignal( bool )

  def __init__( self, conf=None ):

    QObject.__init__( self )

    worldsmanager = QApplication.instance().core.worlds
    if not conf:
      conf = worldsmanager.newWorldConf()

    self.conf    = conf
    self.worldui = None
    self.logger  = None

    self.input = []
    self.input_flush = SingleShotTimer( self.flushPendingInput )

    self.was_logging       = False
    self.last_log_filename = None

    self.connected.connect( self.connectionStatusChanged )

    self.status = Status.DISCONNECTED

    self.socketpipeline = SocketPipeline( conf )
    self.socketpipeline.addSink( self.sink, ChunkData.NETWORK )

    self.conf_observer = ConfigObserver( self.conf )


  def title( self ):

    conf = self.conf
    return conf._name or u"(%s:%d)" % ( conf._host, conf._port )


  def host( self ):

    return self.conf._host


  def save( self ):

    QApplication.instance().core.worlds.saveWorld( self )


  def setUI( self, worldui ):

    self.worldui = worldui
    self.worldui.updateToolBarIcons( self.conf._toolbar_icon_size )
    self.conf_observer.addCallback( "toolbar_icon_size",
                                    self.worldui.updateToolBarIcons )


  def isAnonymous( self ):

    return self.conf.isAnonymous()


  def info( self, text ):

    if self.worldui:
      self.worldui.output_manager.insertInfoText( text )


  def connectToWorld( self ):

    if not self.isConnected():
      self.socketpipeline.connectToHost()


  def disconnectFromWorld( self ):

    if self.isConnected():

      messagebox = QMessageBox( self.worldui.window() )
      messagebox.setWindowTitle( u"Confirm disconnect" )
      messagebox.setIcon( QMessageBox.Question )
      messagebox.setText( u"Really disconnect from this world?" )
      messagebox.addButton( u"Disconnect", QMessageBox.AcceptRole )
      messagebox.addButton( QMessageBox.Cancel )

      if messagebox.exec_() == QMessageBox.Cancel:
        return

    self.ensureWorldDisconnected()


  def ensureWorldDisconnected( self ):

    ## TODO: Is this really necessary anymore?

    if self.isConnected():
      self.socketpipeline.disconnectFromHost()

    else:
      self.socketpipeline.abort()


  @pyqtSlot()
  def connectionStatusChanged( self ):

    if self.status == Status.CONNECTED:

      if self.conf._autolog or self.was_logging:
        self.startLogging()

    elif self.status == Status.DISCONNECTED:

      self.was_logging = ( self.logger is not None )
      self.stopLogging()


  def computeLogFileName( self ):

    logfile = self.conf._logfile_name
    logdir  = self.conf._logfile_dir

    logfile = time.strftime( logfile )
    logfile = logfile.replace( u"[WORLDNAME]", self.title() )
    logfile = ensure_valid_filename( logfile )
    logfile = os.path.join( logdir, logfile )

    if not os.path.exists( logfile ):
      ## File name is available. Good!
      return logfile

    base, ext = os.path.splitext( logfile )

    if self.last_log_filename and self.last_log_filename.startswith( base ):
      ## File exists but already seems to belong to this session. Keep using
      ## it.
      return self.last_log_filename

    ## File exists. Compute an available variant in the form "filename_X.ext".
    candidate = base + u"_%d" + ext
    existing  = set( glob( base + u"_*" + ext ) )

    possible_filenames = [ candidate % i
                             for i in range( 1, len( existing ) + 2 )
                             if candidate % i not in existing ]

    logfile = possible_filenames[ 0 ]

    return logfile


  def startLogging( self ):

    ## TODO: Prompt for a logfile name if none is recorded in config

    logfile = self.computeLogFileName()

    if self.logger:

      if logfile == self.last_log_filename:
        ## We're already logging to the correct file! Good.
        return

      self.logger.stop()
      del self.logger

    self.logger = create_logger_for_world( self, logfile )
    self.last_log_filename = logfile

    if self.logger:
      self.nowLogging.emit( True )
      self.logger.start()


  def stopLogging( self ):

    if not self.logger:
      return

    self.nowLogging.emit( False )
    self.logger.stop()
    self.logger = None


  def sink( self, chunk ):

    previous_status = self.status

    _, payload = chunk

    if   payload in ( ChunkData.RESOLVING, ChunkData.CONNECTING ):
      self.status = Status.CONNECTING

    elif payload == ChunkData.CONNECTED:
      self.status = Status.CONNECTED

    elif payload == ChunkData.DISCONNECTING:
      self.status = Status.DISCONNECTING

    elif payload in (
                      ChunkData.DISCONNECTED,
                      ChunkData.CONNECTIONREFUSED,
                      ChunkData.HOSTNOTFOUND,
                      ChunkData.TIMEOUT,
                      ChunkData.OTHERERROR,
                    ):

      self.status = Status.DISCONNECTED


    if self.status != previous_status:
      self.connected.emit( self.isConnected() )
      self.disconnected.emit( self.isDisconnected() )


  def isConnected( self ):

    return self.status == Status.CONNECTED


  def isDisconnected( self ):

    return self.status == Status.DISCONNECTED


  def selectFile( self, caption=u"Select file", dir=u"", filter=u"" ):

    if not dir:
      dir = platformSpecific.get_homedir()

    return QFileDialog.getOpenFileName( self.worldui, caption, dir, filter )


  def openFileOrErr( self, filename, mode='r' ):

    local_encoding = QApplication.instance().local_encoding
    filename = os.path.expanduser( filename )
    basename = os.path.basename( filename )

    try:
      return file( filename, mode )  ## NB: filename can be unicode. That's OK!

    except ( IOError, OSError ), e:

      errormsg = str( e ).decode( local_encoding, "replace" )
      self.info( u"Error: %s: %s" % ( basename, errormsg ) )
      return None


  def loadFile( self, filename=None, blocksize=2048 ):

    if filename is None:

      filename = self.selectFile(
                                  caption = u"Select the file to load",
                                  filter  = u"Text files (*.log *.txt)" \
                                            u";;All files (*)"
                                )

      filename = unicode( filename )  ## QString -> unicode

    if not filename:
      return

    f = self.openFileOrErr( filename )

    if not f:
      return

    self.info( u"Loading %s..." % os.path.basename( filename ) )

    t1 = time.time()

    while True:

      data = f.read( blocksize )

      if not data:
        break

      self.socketpipeline.pipeline.feedBytes( data, blocksize )

    t2 = time.time()

    f.close()

    self.info( u"File loaded in %.2fs." % ( t2 - t1 ) )


  def flushPendingInput( self ):

    while self.input:

      text = self.input.pop( 0 )

      if text.startswith( CMDCHAR ):
        QApplication.instance().core.commands.runCmdLine( self, text[ len( CMDCHAR ): ] )

      else:
        self.socketpipeline.send( text + u"\r\n" )


  def processInput( self, input ):

    for line in input.split( u'\n' ):
      self.input.append( line )

    self.input_flush.start()


  def __del__( self ):

    self.worldui        = None
    self.socketpipeline = None
    self.logger         = None
