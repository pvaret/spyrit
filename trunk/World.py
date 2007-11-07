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


from localqt        import *
from PipelineChunks import *

from Utilities      import check_ssl_is_available

from Singletons     import singletons
from SocketPipeline import SocketPipeline


class World:

  def __init__( s, conf=None ):

    if not conf: conf = singletons.worldsmanager.newWorldConf()

    ## TODO: Update all this when a conf change SIGNAL is emitted.

    s.conf    = conf
    s.worldui = None

    ## We need both of the following values, because there are cases (for
    ## instance, when resolving the server name) where we can't consider
    ## ourselves connected nor disconnected.

    s.connected    = False
    s.disconnected = True

    ## Aliased for convenience.

    s.name = conf._name
    s.host = conf._host
    s.port = conf._port
    s.ssl  = check_ssl_is_available() and conf._ssl

    s.displayname = s.name or "(%s:%d)" % ( s.host, s.port )

    s.socketpipeline = SocketPipeline( s.host, s.port, s.ssl )
    s.socketpipeline.addSink( s.sink, [ chunktypes.NETWORK ] )


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


  def ensureWorldDisconnected( s ):

    if s.connected:
      s.socketpipeline.disconnectFromHost()
      
    else:
      s.socketpipeline.abort()


  def setConnected( s ):

    s.connected = True


  def setDisconnected( s ):

    s.connected = False


  def sink( s, chunks ):

    for chunk in chunks:

      if   chunk.data == NetworkChunk.CONNECTED:

        QtCore.QTimer.singleShot( 0, s.setConnected )

      elif chunk.data == NetworkChunk.DISCONNECTED:

        QtCore.QTimer.singleShot( 0, s.setDisconnected )

      s.disconnected = ( chunk.data == NetworkChunk.DISCONNECTED )


  def close( s ):

    if s.worldui:
      singletons.mw.closeWorld( s.worldui )
