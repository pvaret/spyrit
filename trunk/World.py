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
## World.py
##
## Holds the class that manages the state of a world: input, output, connection
## and disconnection, etc.
##


import os
import time

from localqt          import *
from PipelineChunks   import *

from Utilities        import check_ssl_is_available

from Singletons       import singletons
from SocketPipeline   import SocketPipeline

from PlatformSpecific import platformSpecific

from Logger           import Logger



class World( QtCore.QObject ):

  def __init__( s, conf=None ):

    QtCore.QObject.__init__( s )

    if not conf: conf = singletons.worldsmanager.newWorldConf()

    s.conf    = conf
    s.worldui = None
    s.logger  = Logger( s )
    
    connect( s, SIGNAL( "connected( bool )" ), s.logger.connectionSlot ) 

    ## We need both of the following values, because there are cases (for
    ## instance, when resolving the server name) where we can't consider
    ## ourselves connected nor disconnected.

    s.connected    = False
    s.disconnected = True

    s.socketpipeline = SocketPipeline( conf )
    s.socketpipeline.addSink( s.sink )
    s.socketpipeline.addSink( s.logger.logOutput )


  def title( s ):

    conf = s.conf
    return conf._name or "(%s:%d)" % ( conf._host, conf._port )


  def host( s ):

    return s.conf._host


  def save( s ):

    singletons.worldsmanager.saveWorld( s )


  def setUI( s, worldui ):

    s.worldui = worldui


  def isAnonymous( s ):

    return s.conf.isAnonymous()


  def info( s, text ):

    if s.worldui:
      s.worldui.outputui.insertInfoText( text )


  def connectToWorld( s ):

    if not s.connected:
      s.socketpipeline.connectToHost()


  def disconnectFromWorld( s ):

    if s.connected:
    
      messagebox = QtGui.QMessageBox( singletons.mw )
      messagebox.setWindowTitle( "Confirm disconnect" )
      messagebox.setIcon( QtGui.QMessageBox.Question )
      messagebox.setText( "Really disconnect from this world?" )
      messagebox.addButton( "Disconnect", QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( QtGui.QMessageBox.Cancel )

      if messagebox.exec_() == QtGui.QMessageBox.Cancel:
        return

    s.ensureWorldDisconnected()


  def ensureWorldDisconnected( s ):

    if s.connected:
      s.socketpipeline.disconnectFromHost()
      
    else:
      s.socketpipeline.abort()


  def setConnected( s ):

    s.connected = True


  def setDisconnected( s ):

    s.connected = False


  def startLogging( s ):

    ## TODO: Prompt for a logfile name if none is recorded in config

    logfile = s.conf._logfile_name
    logdir  = s.conf._logfile_dir

    logfile = time.strftime( logfile )
    logfile = logfile.replace( "[WORLDNAME]", s.title() )

    s.logger.startLogging( os.path.join( logdir, logfile ) )


  def stopLogging( s ):

    s.logger.stopLogging()


  def sink( s, chunks ):

    for chunk in chunks:
      
      if not chunk.chunktype == ChunkTypes.NETWORK:
        continue

      if   chunk.data == NetworkChunk.CONNECTED:

        QtCore.QTimer.singleShot( 0, s.setConnected )

      elif chunk.data == NetworkChunk.DISCONNECTED:

        QtCore.QTimer.singleShot( 0, s.setDisconnected )

      s.disconnected = ( chunk.data in ( 
                                         NetworkChunk.DISCONNECTED,
                                         NetworkChunk.HOSTNOTFOUND,
                                         NetworkChunk.TIMEOUT,
                                         NetworkChunk.CONNECTIONREFUSED,
                                       ) )

      emit( s, SIGNAL( "connected( bool )" ), not s.disconnected )


  def selectFile( s, caption="Select file", dir="", filter="" ):

    if not dir:
      dir = platformSpecific.get_homedir()

    return QtGui.QFileDialog.getOpenFileName( s.worldui, caption, dir, filter )


  def loadFile( s, filename=None ):

    local_encoding = qApp().local_encoding

    if filename is None:
      filename = s.selectFile(
                               caption = "Select the file to load",
                               filter  = "Text files (*.log *.txt)" \
                                       + ";;All files (*)"
                             )

    filename = str( filename )
    basename = os.path.basename( filename ).decode( local_encoding, "replace" )

    if not filename: return

    try:
      f = file( filename )

    except IOError, e:

      errormsg = e.strerror.decode( local_encoding, "replace" )
      s.info( "Error: %s: %s" % ( basename, errormsg ) )
      return

    s.info( "Loading %s..." % basename )

    t1 = time.time()

    while True:

      data = f.read( 4096 )
      if not data: break
      s.socketpipeline.pipeline.feedBytes( data )
      qApp().processEvents()

    t2 = time.time()

    f.close()

    s.info( "File loaded in %.2fs." % ( t2 - t1 ) )


  def __del__( s ):

    s.worldui        = None
    s.socketpipeline = None
    s.logger         = None
