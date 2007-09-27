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
## SocketPipeline.py
##
## This file holds the SocketPipeline class, which connects a Pipeline to a
## socket and manages connection/disconnection and everything.
##


from localqt import *

from Pipeline        import *
from PipelineChunks  import *
from PipelineFilters import *
from Logger          import logger


class SocketPipeline:

  def __init__( s, host, port, ssl=False ):

    s.pipeline = Pipeline()
    s.pipeline.addFilter( TelnetFilter() )
    s.pipeline.addFilter( AnsiFilter() )
    s.pipeline.addFilter( EndLineFilter() )
    s.pipeline.addFilter( UnicodeTextFilter() )

    s.host = host
    s.port = port
    s.ssl  = ssl

    if s.ssl:

      s.socket = QtNetwork.QSslSocket()

      connect( s.socket, SIGNAL( "encrypted()" ), s.reportEncrypted )
      connect( s.socket, SIGNAL( "sslErrors( const QList<QSslError> & )" ),
                         s.handleSslErrors )

    else:
      s.socket = QtNetwork.QTcpSocket()

    connect( s.socket, SIGNAL( "stateChanged( QAbstractSocket::SocketState )" ),
                       s.reportStateChange )
    connect( s.socket, SIGNAL( "error( QAbstractSocket::SocketError )" ),
                       s.reportError )
    connect( s.socket, SIGNAL( "readyRead()" ), s.readSocket )


  def connectToHost( s ):

    if s.ssl:
      s.socket.connectToHostEncrypted( s.host, s.port )

    else:
      s.socket.connectToHost( s.host, s.port )


  def disconnectFromHost( s ):

    s.socket.disconnectFromHost()
  
  
  def abort( s ):
    
    s.socket.abort()
    s.socket.close()


  def reportStateChange( s, state ):

    if   state == QtNetwork.QAbstractSocket.HostLookupState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.RESOLVING ) )

    elif state == QtNetwork.QAbstractSocket.ConnectingState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.CONNECTING ) )

    elif state == QtNetwork.QAbstractSocket.ConnectedState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.CONNECTED ) )

    elif state == QtNetwork.QAbstractSocket.UnconnectedState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.DISCONNECTED ) )


  def reportEncrypted( s ):

    s.pipeline.feedChunk( NetworkChunk( NetworkChunk.ENCRYPTED ) )


  def reportError( s, error ):

    if   error == QtNetwork.QAbstractSocket.ConnectionRefusedError:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.CONNECTIONREFUSED ) )

    elif error == QtNetwork.QAbstractSocket.HostNotFoundError:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.HOSTNOTFOUND ) )

    elif error == QtNetwork.QAbstractSocket.SocketTimeoutError:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.TIMEOUT ) )

    elif error == QtNetwork.QAbstractSocket.RemoteHostClosedError:
      pass  ## It's okay, we handle it as a disconnect.

    else:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.OTHERERROR ) )


  def handleSslErrors( s, errors ):

    ## We take note of the errors... and then discard them.
    ## SSL validation errors are very common because many legitimate servers
    ## are just not going to fork money over certificates, and nobody's
    ## going to blame them for it.

    for err in errors:
      logger.warn( "SSL Error: " + err.errorString() )

    s.socket.ignoreSslErrors()


  def readSocket( s ):

    data = str( s.socket.readAll() )
    s.pipeline.feedBytes( data )


  def send( s, data ):

    assert type( data ) is type( u'' )
    data = s.pipeline.formatForSending( data )

    s.socket.write( data )
    s.socket.flush()


  def addSink( s, sink, filter=None ):

    if filter is None:
      s.pipeline.addSink( sink )

    else:
      if type( filter ) not in ( type( [] ), type( () ) ):
        filter = [ filter ]

      def filteredsink( chunks ):
        chunks = [ chunk for chunk in chunks if chunk.chunktype in filter ]
        if chunks: return sink( chunks )

      s.pipeline.addSink( filteredsink )