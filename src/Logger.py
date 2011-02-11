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
import time

from os.path import basename, dirname, isdir

from localqt     import *
from FormatStack import FormatStack
from Globals     import FORMAT_PROPERTIES
from Globals     import ESC
from Globals     import compute_closest_ansi_color

from pipeline    import ChunkData


class PlainLogger:

  log_chunk_types = ChunkData.TEXT | ChunkData.FLOWCONTROL
  encoding = "utf-8"


  def __init__( s, world, logfile ):

    s.world   = world
    s.logfile = logfile

    s.is_logging = False
    s.buffer     = []
    #if backlog:
    #  s.buffer.append( backlog )

    s.flush_timer = QtCore.QTimer()
    s.flush_timer.setInterval( 100 )  ## ms
    s.flush_timer.setSingleShot( True )
    connect( s.flush_timer, SIGNAL( 'timeout()' ), s.flushBuffer )


  def logChunk( s, chunk ):

    if not s.is_logging:
      return

    chunk_type, payload = chunk

    if chunk_type == ChunkData.TEXT:
      s.doLogText( payload )

    elif chunk == ( ChunkData.FLOWCONTROL, ChunkData.LINEFEED ):
      s.doLogText( u"\n" )

    else:
      return

    s.flush_timer.start()


  def doLogText( s, text ):

    s.buffer.append( text.encode( s.encoding, "replace" ) )


  def doLogStart( s ):

    now = time.strftime( u'%c', time.localtime() )
    s.doLogText( u"%% Log start for %s on %s.\n" % ( s.world.title(), now ) )


  def doLogStop( s ):

    now = time.strftime( u'%c', time.localtime() )
    s.doLogText( u"%% Log end on %s.\n" % now )


  def flushBuffer( s ):

    if s.is_logging and s.buffer:

      s.logfile.write( "".join( s.buffer ) )
      s.logfile.flush()
      s.buffer[:] = []


  def start( s ):

    if s.is_logging:
      return

    s.is_logging = True
    s.doLogStart()
    ## TODO: move info message out of logger?
    s.world.info( u"Started logging to %s" % basename( s.logfile.name ) )

    s.flushBuffer()


  def stop( s ):

    if not s.is_logging:
      return

    s.doLogStop()
    ## TODO: move info message out of logger?
    s.world.info( u"Stopped logging." )

    s.flushBuffer()
    s.is_logging = False


  def __del__( s ):

     s.stop()

     s.world   = None
     s.logfile = None






class AnsiFormatter:

  def __init__( s, buffer ):

    s.buffer = buffer


  def setProperty( s, property, value ):

    if   property == FORMAT_PROPERTIES.BOLD:
        s.buffer.append( ESC + "[1m" )

    elif property == FORMAT_PROPERTIES.ITALIC:
        s.buffer.append( ESC + "[3m" )

    elif property == FORMAT_PROPERTIES.UNDERLINE:
        s.buffer.append( ESC + "[4m" )

    elif property == FORMAT_PROPERTIES.COLOR:

        ansi_color = compute_closest_ansi_color( value )
        s.buffer.append( ESC + "[38;5;%dm" % ansi_color )

    elif property == FORMAT_PROPERTIES.BACKGROUND:

        ansi_color = compute_closest_ansi_color( value )
        s.buffer.append( ESC + "[48;5;%dm" % ansi_color )



  def clearProperty( s, property ):

    if   property == FORMAT_PROPERTIES.BOLD:
        s.buffer.append( ESC + "[22m" )

    elif property == FORMAT_PROPERTIES.ITALIC:
        s.buffer.append( ESC + "[23m" )

    elif property == FORMAT_PROPERTIES.UNDERLINE:
        s.buffer.append( ESC + "[24m" )

    elif property == FORMAT_PROPERTIES.COLOR:
        s.buffer.append( ESC + "[39m" )

    elif property == FORMAT_PROPERTIES.BACKGROUND:
        s.buffer.append( ESC + "[49m" )



class AnsiLogger( PlainLogger ):

  log_chunk_types = PlainLogger.log_chunk_types \
                  | ChunkData.HIGHLIGHT | ChunkData.ANSI


  def __init__( s, *args ):

    PlainLogger.__init__( s, *args )

    s.format_stack = FormatStack( AnsiFormatter( s.buffer ) )


  def logChunk( s, chunk ):

    chunk_type, payload = chunk

    if chunk_type & ( ChunkData.HIGHLIGHT | ChunkData.ANSI ):
      s.format_stack.processChunk( chunk )

    else:
      PlainLogger.logChunk( s, chunk )


  def doLogStop( s ):

    s.buffer.append( ESC + "[m" )
    PlainLogger.doLogStop( s )




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

  if world.conf._log_ansi:
    LoggerClass = AnsiLogger
  else:
    LoggerClass = PlainLogger

  logger = LoggerClass( world, file )

  world.socketpipeline.addSink( logger.logChunk, logger.log_chunk_types )

  return logger
