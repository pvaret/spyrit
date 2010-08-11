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
## Logger.py
##
## Holds the class that manages logging of a world's output to a text file.
##


import os
from os.path import basename, dirname, isdir

from localqt import *

import ChunkData


class PlainLogger:

  log_chunk_types = ChunkData.TEXT | ChunkData.FLOWCONTROL

  def __init__( s, world, logfile ):

    s.world   = world
    s.logfile = logfile

    s.is_logging = False
    s.buffer     = []
    #if backlog:
    #  s.buffer.append( backlog )


  def logChunk( s, chunk ):

    ## Don't buffer data if there is no logfile to send it to.
    if not s.is_logging:
      return

    chunk_type, payload = chunk

    if chunk_type == ChunkData.TEXT:
      s.buffer.append( payload.encode( "utf-8", "replace" ) )

    elif chunk == ( ChunkData.FLOWCONTROL, ChunkData.LINEFEED ):
      s.buffer.append( "\n" )

    QtCore.QTimer.singleShot( 0, s.flushBuffer )


  def flushBuffer( s ):

    if s.is_logging and s.buffer:

      s.logfile.write( "".join( s.buffer ) )
      s.logfile.flush()
      s.buffer = []


  def start( s ):

    ## TODO: handle toolbar / statusbar related stuff

    if s.is_logging:
      return

    ## TODO: move info message out of logger?
    s.world.info( u"Started logging to %s" % basename( s.logfile.name ) )

    if s.buffer:
      s.flushBuffer()

    s.is_logging = True


  def stop( s ):

    if not s.is_logging:
      return

    ## TODO: handle toolbar / statusbar related stuff

    s.flushBuffer()
    s.is_logging = False

    ## TODO: move info message out of logger?
    s.world.info( u"Stopped logging." )


  def __del__( s ):

     s.stop()

     s.world   = None
     s.logfile = None



def create_logger_for_world( world, logfile ):

  dir = dirname( logfile )

  if not isdir( dir ):

    try:
      os.makedirs( dir )

    except ( IOError, OSError ):
      pass

  file = world.openFileOrErr( logfile, 'a+' )

  if not file:
    return None

  logger = PlainLogger( world, file )

  world.socketpipeline.addSink( logger.logChunk, logger.log_chunk_types )

  return logger
