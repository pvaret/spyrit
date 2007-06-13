##
## World.py
##
## Holds the class that manages the state of a world: input, output, connection
## and disconnection, etc.
##


from localqt import *

from PipelineChunks import *
from SocketPipeline import SocketPipeline


class World:

  def __init__( s, conf, name=None ):

    s.name = name
    s.conf = conf

    s.connected = False

    s.host = conf._host
    s.port = conf._port

    s.displayname = name or "(%s:%d)" % ( s.host, s.port )

    s.socketpipeline = SocketPipeline( s.host, s.port )
    s.socketpipeline.addSink( s.sink, [ chunktypes.NETWORK ] )


  def connectToWorld( s ):

    s.socketpipeline.connectToHost()


  def disconnectFromWorld( s ):

    s.socketpipeline.disconnectFromHost()


  def sink( s, chunks ):

    for chunk in chunks:

      if   chunk.data == NetworkChunk.CONNECTED:
        s.connected = True

      elif chunk.data == NetworkChunk.DISCONNECTED:
        s.connected = False
