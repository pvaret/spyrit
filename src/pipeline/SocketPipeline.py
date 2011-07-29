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
## SocketPipeline.py
##
## This file holds the SocketPipeline class, which connects a Pipeline to a
## socket and manages connection/disconnection and everything.
##

from PyQt4.QtCore    import pyqtSlot
from PyQt4.QtGui     import QApplication
from PyQt4.QtNetwork import QSslSocket
from PyQt4.QtNetwork import QTcpSocket
from PyQt4.QtNetwork import QAbstractSocket

from Pipeline          import Pipeline
from AnsiFilter        import AnsiFilter
from TelnetFilter      import TelnetFilter
from TriggersFilter    import TriggersFilter
from SingleShotTimer   import SingleShotTimer
from FlowControlFilter import FlowControlFilter
from UnicodeTextFilter import UnicodeTextFilter

from Messages  import messages
from Utilities import check_ssl_is_available

import ChunkData



class SocketPipeline:

  def __init__( self, settings ):

    self.net_settings = settings._net

    self.triggersmanager = QApplication.instance().core.triggers

    self.pipeline = Pipeline()

    self.pipeline.addFilter( TelnetFilter )
    self.pipeline.addFilter( AnsiFilter )
    self.pipeline.addFilter( UnicodeTextFilter, encoding=self.net_settings._encoding )
    self.pipeline.addFilter( FlowControlFilter )
    self.pipeline.addFilter( TriggersFilter, manager=self.triggersmanager )

    self.using_ssl = False
    self.socket    = None
    self.buffer    = []

    self.flush_timer = SingleShotTimer( self.flushBuffer )

    self.net_settings.onChange( "encoding", self.setStreamEncoding )


  def setStreamEncoding( self ):

    if self.pipeline:
      self.pipeline.notify( "encoding_changed", self.net_settings._encoding )


  def setupSocket( self ):

    if self.net_settings._ssl and check_ssl_is_available():

      self.using_ssl = True
      self.socket    = QSslSocket()

      self.socket.encrypted.connect( self.reportEncrypted )
      self.socket.sslErrors.connect( self.handleSslErrors )

    else:
      self.socket = QTcpSocket()

      if self.net_settings._ssl:  ## SSL was requested but is not available...
        messages.warn( u"SSL functions not available; attempting" \
                       u"unencrypted connection instead..." )

    self.socket.stateChanged.connect( self.reportStateChange )
    self.socket.error.connect( self.reportError )
    self.socket.readyRead.connect( self.readSocket )


  def connectToHost( self ):

    if not self.socket:
      self.setupSocket()

    self.pipeline.resetInternalState()

    params = ( self.net_settings._host, self.net_settings._port )

    if self.using_ssl:
      self.socket.connectToHostEncrypted( *params )

    else:
      self.socket.connectToHost( *params )


  def disconnectFromHost( self ):

    self.socket.disconnectFromHost()


  def abort( self ):

    self.socket.abort()
    self.socket.close()


  @pyqtSlot( "QAbstractSocket::SocketState" )
  def reportStateChange( self, state ):

    self.flushBuffer()

    if   state == QAbstractSocket.HostLookupState:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.RESOLVING ) )

    elif state == QAbstractSocket.ConnectingState:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.CONNECTING ) )

    elif state == QAbstractSocket.ConnectedState:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.CONNECTED ) )

    elif state == QAbstractSocket.UnconnectedState:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.DISCONNECTED ) )


  @pyqtSlot()
  def reportEncrypted( self ):

    self.flushBuffer()
    self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.ENCRYPTED ) )


  @pyqtSlot( "QAbstractSocket::SocketError" )
  def reportError( self, error ):

    self.flushBuffer()

    if   error == QAbstractSocket.ConnectionRefusedError:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.CONNECTIONREFUSED ) )

    elif error == QAbstractSocket.HostNotFoundError:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.HOSTNOTFOUND ) )

    elif error == QAbstractSocket.SocketTimeoutError:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.TIMEOUT ) )

    elif error == QAbstractSocket.RemoteHostClosedError:
      pass  ## It's okay, we handle it as a disconnect.

    else:
      self.pipeline.feedChunk( ( ChunkData.NETWORK, ChunkData.OTHERERROR ) )


  @pyqtSlot( "const QList<QSslError> &" )
  def handleSslErrors( self, errors ):

    ## We take note of the errors... and then discard them.
    ## SSL validation errors are very common because many legitimate servers
    ## are just not going to fork money over certificates, and nobody's
    ## going to blame them for it.

    for err in errors:
      messages.warn( u"SSL Error: " + err.errorString() )

    self.socket.ignoreSslErrors()


  @pyqtSlot()
  def readSocket( self ):

    data = str( self.socket.readAll() )
    self.buffer.append( data )

    self.flush_timer.start()


  def flushBuffer( self ):

    data = ''.join( self.buffer )
    del self.buffer[:]
    self.pipeline.feedBytes( data )


  def send( self, data ):

    assert isinstance( data, unicode )

    if not self.socket.state() == self.socket.ConnectedState:

      ## Don't write anything if the socket is not connected.
      return

    data = self.pipeline.formatForSending( data )

    self.socket.write( data )
    self.socket.flush()


  def addSink( self, sink, types=ChunkData.ALL_TYPES ):

    self.pipeline.addSink( sink, types )


  def __del__( self ):

    self.socket   = None
    self.pipeline = None
