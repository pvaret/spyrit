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
#from PyQt4.QtCore import pyqtSlot
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

  def __init__( s, conf=None ):

    QObject.__init__( s )

    worldsmanager = QApplication.instance().core.worlds
    if not conf:
      conf = worldsmanager.newWorldConf()

    s.conf    = conf
    s.worldui = None
    s.logger  = None

    s.input = []
    s.input_flush = SingleShotTimer( s.flushPendingInput )

    s.was_logging       = False
    s.last_log_filename = None

    s.connected.connect( s.connectionStatusChanged )

    s.status = Status.DISCONNECTED

    s.socketpipeline = SocketPipeline( conf )
    s.socketpipeline.addSink( s.sink, ChunkData.NETWORK )

    s.conf_observer = ConfigObserver( s.conf )


  def title( s ):

    conf = s.conf
    return conf._name or u"(%s:%d)" % ( conf._host, conf._port )


  def host( s ):

    return s.conf._host


  def save( s ):

    QApplication.instance().core.worlds.saveWorld( s )


  def setUI( s, worldui ):

    s.worldui = worldui
    s.worldui.updateToolBarIcons( s.conf._toolbar_icon_size )
    s.conf_observer.addCallback( "toolbar_icon_size",
                                 s.worldui.updateToolBarIcons )


  def isAnonymous( s ):

    return s.conf.isAnonymous()


  def info( s, text ):

    if s.worldui:
      s.worldui.output_manager.insertInfoText( text )


  def connectToWorld( s ):

    if not s.isConnected():
      s.socketpipeline.connectToHost()


  def disconnectFromWorld( s ):

    if s.isConnected():

      messagebox = QMessageBox( s.worldui.window() )
      messagebox.setWindowTitle( u"Confirm disconnect" )
      messagebox.setIcon( QMessageBox.Question )
      messagebox.setText( u"Really disconnect from this world?" )
      messagebox.addButton( u"Disconnect", QMessageBox.AcceptRole )
      messagebox.addButton( QMessageBox.Cancel )

      if messagebox.exec_() == QMessageBox.Cancel:
        return

    s.ensureWorldDisconnected()


  def ensureWorldDisconnected( s ):

    ## TODO: Is this really necessary anymore?

    if s.isConnected():
      s.socketpipeline.disconnectFromHost()

    else:
      s.socketpipeline.abort()


  #@pyqtSlot()
  def connectionStatusChanged( s ):

    if s.status == Status.CONNECTED:

      if s.conf._autolog or s.was_logging:
        s.startLogging()

    elif s.status == Status.DISCONNECTED:

      s.was_logging = ( s.logger is not None )
      s.stopLogging()


  def computeLogFileName( s ):

    logfile = s.conf._logfile_name
    logdir  = s.conf._logfile_dir

    logfile = time.strftime( logfile )
    logfile = logfile.replace( u"[WORLDNAME]", s.title() )
    logfile = ensure_valid_filename( logfile )
    logfile = os.path.join( logdir, logfile )

    if not os.path.exists( logfile ):
      ## File name is available. Good!
      return logfile

    base, ext = os.path.splitext( logfile )

    if s.last_log_filename and s.last_log_filename.startswith( base ):
      ## File exists but already seems to belong to this session. Keep using
      ## it.
      return s.last_log_filename

    ## File exists. Compute an available variant in the form "filename_X.ext".
    candidate = base + u"_%d" + ext
    existing  = set( glob( base + u"_*" + ext ) )

    possible_filenames = [ candidate % i
                             for i in range( 1, len( existing ) + 2 )
                             if candidate % i not in existing ]

    logfile = possible_filenames[ 0 ]

    return logfile


  def startLogging( s ):

    ## TODO: Prompt for a logfile name if none is recorded in config

    logfile = s.computeLogFileName()

    if s.logger:

      if logfile == s.last_log_filename:
        ## We're already logging to the correct file! Good.
        return

      s.logger.stop()
      del s.logger

    s.logger = create_logger_for_world( s, logfile )
    s.last_log_filename = logfile

    if s.logger:
      s.nowLogging.emit( True )
      s.logger.start()


  def stopLogging( s ):

    if not s.logger:
      return

    s.nowLogging.emit( False )
    s.logger.stop()
    s.logger = None


  def sink( s, chunk ):

    previous_status = s.status

    _, payload = chunk

    if   payload in ( ChunkData.RESOLVING, ChunkData.CONNECTING ):
      s.status = Status.CONNECTING

    elif payload == ChunkData.CONNECTED:
      s.status = Status.CONNECTED

    elif payload == ChunkData.DISCONNECTING:
      s.status = Status.DISCONNECTING

    elif payload in (
                      ChunkData.DISCONNECTED,
                      ChunkData.CONNECTIONREFUSED,
                      ChunkData.HOSTNOTFOUND,
                      ChunkData.TIMEOUT,
                      ChunkData.OTHERERROR,
                    ):

      s.status = Status.DISCONNECTED


    if s.status != previous_status:
      s.connected.emit( s.isConnected() )
      s.disconnected.emit( s.isDisconnected() )


  def isConnected( s ):

    return s.status == Status.CONNECTED


  def isDisconnected( s ):

    return s.status == Status.DISCONNECTED


  def selectFile( s, caption=u"Select file", dir=u"", filter=u"" ):

    if not dir:
      dir = platformSpecific.get_homedir()

    return QFileDialog.getOpenFileName( s.worldui, caption, dir, filter )


  def openFileOrErr( s, filename, mode='r' ):

    local_encoding = QApplication.instance().local_encoding
    filename = os.path.expanduser( filename )
    basename = os.path.basename( filename )

    try:
      return file( filename, mode )  ## NB: filename can be unicode. That's OK!

    except ( IOError, OSError ), e:

      errormsg = str( e ).decode( local_encoding, "replace" )
      s.info( u"Error: %s: %s" % ( basename, errormsg ) )
      return None


  def loadFile( s, filename=None, blocksize=2048 ):

    if filename is None:

      filename = s.selectFile(
                               caption = u"Select the file to load",
                               filter  = u"Text files (*.log *.txt)" \
                                         u";;All files (*)"
                             )

      filename = unicode( filename )  ## QString -> unicode

    if not filename:
      return

    f = s.openFileOrErr( filename )

    if not f:
      return

    s.info( u"Loading %s..." % os.path.basename( filename ) )

    t1 = time.time()

    while True:

      data = f.read( blocksize )

      if not data:
        break

      s.socketpipeline.pipeline.feedBytes( data, blocksize )

    t2 = time.time()

    f.close()

    s.info( u"File loaded in %.2fs." % ( t2 - t1 ) )


  def flushPendingInput( s ):

    while s.input:

      text = s.input.pop( 0 )

      if text.startswith( CMDCHAR ):
        QApplication.instance().core.commands.runCmdLine( s, text[ len( CMDCHAR ): ] )

      else:
        s.socketpipeline.send( text + u"\r\n" )


  def processInput( s, input ):

    for line in input.split( u'\n' ):
      s.input.append( line )

    s.input_flush.start()


  def __del__( s ):

    s.worldui        = None
    s.socketpipeline = None
    s.logger         = None
