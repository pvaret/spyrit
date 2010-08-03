# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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



class Status:

  DISCONNECTED  = 0
  CONNECTING    = 1
  CONNECTED     = 2
  DISCONNECTING = 3


class World( QtCore.QObject ):

  def __init__( s, conf=None ):

    QtCore.QObject.__init__( s )

    if not conf: conf = singletons.worldsmanager.newWorldConf()

    s.conf    = conf
    s.worldui = None
    s.logger  = Logger( s )

    connect( s, SIGNAL( "connected( bool )" ), s.connectionStatusChanged )

    s.status = Status.DISCONNECTED

    s.socketpipeline = SocketPipeline( conf )
    s.socketpipeline.addSink( s.sink, ChunkTypes.NETWORK )
    s.socketpipeline.addSink( s.logger.logOutput,
                              ChunkTypes.TEXT | ChunkTypes.FLOWCONTROL )


  def title( s ):

    conf = s.conf
    return conf._name or u"(%s:%d)" % ( conf._host, conf._port )


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
      s.worldui.output_manager.insertInfoText( text )


  def connectToWorld( s ):

    if not s.isConnected():
      s.socketpipeline.connectToHost()


  def disconnectFromWorld( s ):

    if s.isConnected():

      messagebox = QtGui.QMessageBox( singletons.mw )
      messagebox.setWindowTitle( u"Confirm disconnect" )
      messagebox.setIcon( QtGui.QMessageBox.Question )
      messagebox.setText( u"Really disconnect from this world?" )
      messagebox.addButton( u"Disconnect", QtGui.QMessageBox.AcceptRole )
      messagebox.addButton( QtGui.QMessageBox.Cancel )

      if messagebox.exec_() == QtGui.QMessageBox.Cancel:
        return

    s.ensureWorldDisconnected()


  def ensureWorldDisconnected( s ):

    if s.isConnected():
      s.socketpipeline.disconnectFromHost()

    else:
      s.socketpipeline.abort()


  def connectionStatusChanged( s, connected ):

    if connected:

      if s.conf._autolog:
        s.startLogging()

    else:
      s.stopLogging()


  def startLogging( s ):

    ## TODO: Prompt for a logfile name if none is recorded in config

    logfile = s.conf._logfile_name
    logdir  = s.conf._logfile_dir

    logfile = time.strftime( logfile )
    logfile = logfile.replace( u"[WORLDNAME]", s.title() )

    s.logger.startLogging( os.path.join( logdir, logfile ) )


  def stopLogging( s ):

    s.logger.stopLogging()


  def sink( s, chunk ):

    previous_status = s.status

    if   chunk.data in ( NetworkChunk.RESOLVING, NetworkChunk.CONNECTING ):

      s.status = Status.CONNECTING

    elif chunk.data == NetworkChunk.CONNECTED:

      s.status = Status.CONNECTED

    elif chunk.data == NetworkChunk.DISCONNECTING:

      s.status = Status.DISCONNECTING

    elif chunk.data in (
                          NetworkChunk.DISCONNECTED,
                          NetworkChunk.CONNECTIONREFUSED,
                          NetworkChunk.HOSTNOTFOUND,
                          NetworkChunk.TIMEOUT,
                          NetworkChunk.OTHERERROR,
                       ):

      s.status = Status.DISCONNECTED


    if s.status != previous_status:
      emit( s, SIGNAL( "connected( bool )" ),    s.isConnected() )
      emit( s, SIGNAL( "disconnected( bool )" ), s.isDisconnected() )


  def isConnected( s ):

    return s.status == Status.CONNECTED


  def isDisconnected( s ):

    return s.status == Status.DISCONNECTED


  def selectFile( s, caption=u"Select file", dir=u"", filter=u"" ):

    if not dir:
      dir = platformSpecific.get_homedir()

    return QtGui.QFileDialog.getOpenFileName( s.worldui, caption, dir, filter )


  def openFileOrErr( s, filename ):

    local_encoding = qApp().local_encoding
    basename = os.path.basename( filename )

    try:
      return file( filename )  ## Note: filename can be unicode. This is OK!

    except IOError, e:

      errormsg = e.strerror.decode( local_encoding, "replace" )
      s.info( u"Error: %s: %s" % ( basename, errormsg ) )
      return None


  def loadFile( s, filename=None ):

    if filename is None:

      filename = s.selectFile(
                               caption = u"Select the file to load",
                               filter  = u"Text files (*.log *.txt)" \
                                         u";;All files (*)"
                             )

      filename = unicode( filename )  ## QString -> unicode

    if not filename: return

    f = s.openFileOrErr( filename )

    if not f: return

    s.info( u"Loading %s..." % os.path.basename( filename ) )

    t1 = time.time()

    while True:

      data = f.read( 8192 )

      if not data: break
      if not s.socketpipeline: break

      s.socketpipeline.pipeline.feedBytes( data )
      qApp().processEvents()

    t2 = time.time()

    f.close()

    s.info( u"File loaded in %.2fs." % ( t2 - t1 ) )


  def __del__( s ):

    s.worldui        = None
    s.socketpipeline = None
    s.logger         = None
