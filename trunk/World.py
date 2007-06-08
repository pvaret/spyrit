##
## World.py
##
## Holds the class that manages the state of a world: input, output, connection
## and disconnection, etc.
##


from localqt import *

from SocketPipeline import SocketPipeline


class World:

  def __init__( s, config, name=None ):

    s.name   = name
    s.config = config

    host = config._host
    port = config._port

    s.displayname = name or "(%s:%d)" % ( host, port )

    s.socketpipeline = SocketPipeline( host, port )


  def connectToWorld( s ):

    s.socketpipeline.connectToHost()


  def disconnectFromWorld( s ):

    s.socketpipeline.disconnectFromHost()
