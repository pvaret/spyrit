# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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


from __future__ import absolute_import

import os
import time

from os.path import basename, dirname, isdir

from Globals     import ESC
from Globals     import FORMAT_PROPERTIES
from Globals     import compute_closest_ansi_color
from FormatStack import FormatStack

from pipeline.ChunkData import ChunkType
from pipeline.ChunkData import FlowControl

from SingleShotTimer import SingleShotTimer

class PlainLogger:

  log_chunk_types = ChunkType.TEXT | ChunkType.FLOWCONTROL
  encoding = "utf-8"


  def __init__( self, world, logfile ):

    self.world   = world
    self.logfile = logfile

    self.is_logging = False
    self.buffer     = []
    #if backlog:
    #  self.buffer.append( backlog )

    self.flush_timer = SingleShotTimer( self.flushBuffer )
    self.flush_timer.setInterval( 100 )  ## ms


  def logChunk( self, chunk ):

    if not self.is_logging:
      return

    chunk_type, payload = chunk

    if chunk_type == ChunkType.TEXT:
      self.doLogText( payload )

    elif chunk == ( ChunkType.FLOWCONTROL, FlowControl.LINEFEED ):
      self.doLogText( u"\n" )

    else:
      return

    self.flush_timer.start()


  def doLogText( self, text ):

    self.buffer.append( text.encode( self.encoding, "replace" ) )


  def doLogStart( self ):

    now = time.strftime( u'%c', time.localtime() )
    self.doLogText( u"%% Log start for %s on %s.\n" % ( self.world.title(), now ) )


  def doLogStop( self ):

    now = time.strftime( u'%c', time.localtime() )
    self.doLogText( u"%% Log end on %s.\n" % now )


  def flushBuffer( self ):

    if self.is_logging and self.buffer:

      self.logfile.write( "".join( self.buffer ) )
      self.logfile.flush()
      self.buffer[:] = []


  def start( self ):

    if self.is_logging:
      return

    self.is_logging = True
    self.doLogStart()
    ## TODO: move info message out of logger?
    self.world.info( u"Started logging to %s" % basename( self.logfile.name ) )

    self.flushBuffer()


  def stop( self ):

    if not self.is_logging:
      return

    self.doLogStop()
    ## TODO: move info message out of logger?
    self.world.info( u"Stopped logging." )

    self.flushBuffer()
    self.is_logging = False


  def __del__( self ):

     self.stop()






class AnsiFormatter:

  def __init__( self, buffer ):

    self.buffer = buffer


  def setProperty( self, property, value ):

    if   property == FORMAT_PROPERTIES.BOLD:
        self.buffer.append( ESC + "[1m" )

    elif property == FORMAT_PROPERTIES.ITALIC:
        self.buffer.append( ESC + "[3m" )

    elif property == FORMAT_PROPERTIES.UNDERLINE:
        self.buffer.append( ESC + "[4m" )

    elif property == FORMAT_PROPERTIES.COLOR:

        ansi_color = compute_closest_ansi_color( value )
        self.buffer.append( ESC + "[38;5;%dm" % ansi_color )

    elif property == FORMAT_PROPERTIES.BACKGROUND:

        ansi_color = compute_closest_ansi_color( value )
        self.buffer.append( ESC + "[48;5;%dm" % ansi_color )



  def clearProperty( self, property ):

    if   property == FORMAT_PROPERTIES.BOLD:
        self.buffer.append( ESC + "[22m" )

    elif property == FORMAT_PROPERTIES.ITALIC:
        self.buffer.append( ESC + "[23m" )

    elif property == FORMAT_PROPERTIES.UNDERLINE:
        self.buffer.append( ESC + "[24m" )

    elif property == FORMAT_PROPERTIES.COLOR:
        self.buffer.append( ESC + "[39m" )

    elif property == FORMAT_PROPERTIES.BACKGROUND:
        self.buffer.append( ESC + "[49m" )



class AnsiLogger( PlainLogger ):

  log_chunk_types = PlainLogger.log_chunk_types \
                  | ChunkType.HIGHLIGHT | ChunkType.ANSI


  def __init__( self, *args ):

    PlainLogger.__init__( self, *args )

    self.format_stack = FormatStack( AnsiFormatter( self.buffer ) )


  def logChunk( self, chunk ):

    chunk_type, payload = chunk

    if chunk_type & ( ChunkType.HIGHLIGHT | ChunkType.ANSI ):
      self.format_stack.processChunk( chunk )

    else:
      PlainLogger.logChunk( self, chunk )


  def doLogStop( self ):

    self.buffer.append( ESC + "[m" )
    PlainLogger.doLogStop( self )




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

  if world.settings._log._ansi:
    LoggerClass = AnsiLogger
  else:
    LoggerClass = PlainLogger

  logger = LoggerClass( world, file )

  world.socketpipeline.addSink( logger.logChunk, logger.log_chunk_types )

  return logger
