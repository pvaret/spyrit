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


class SocketPipeline:

  def __init__( s, host, port, ssl=False ):

    ## The SSL parameter is unused for now; it's reserved for future Qt 4.3
    ## usage.

    s.pipeline = Pipeline()
    s.pipeline.addFilter( TelnetFilter() )
    s.pipeline.addFilter( AnsiFilter() )
    s.pipeline.addFilter( EndLineFilter() )
    s.pipeline.addFilter( UnicodeTextFilter() )

    s.host = host
    s.port = port

    s.socket = QtNetwork.QTcpSocket()
    connect( s.socket, SIGNAL( "stateChanged( QAbstractSocket::SocketState )" ),
                       s.reportStateChange )
    connect( s.socket, SIGNAL( "error( QAbstractSocket::SocketError )" ),
                       s.reportError )
    connect( s.socket, SIGNAL( "readyRead()" ), s.readSocket )


  def connectToHost( s ):

    s.socket.connectToHost( s.host, s.port )


  def disconnectFromHost( s ):

    s.socket.disconnectFromHost()


  def reportStateChange( s, state ):

    if   state == QtNetwork.QAbstractSocket.HostLookupState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.RESOLVING ) )

    elif state == QtNetwork.QAbstractSocket.ConnectingState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.CONNECTING ) )

    elif state == QtNetwork.QAbstractSocket.ConnectedState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.CONNECTED ) )

    elif state == QtNetwork.QAbstractSocket.UnconnectedState:
      s.pipeline.feedChunk( NetworkChunk( NetworkChunk.DISCONNECTED ) )


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
