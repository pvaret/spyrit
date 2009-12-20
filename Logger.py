# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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
import codecs

from os.path        import basename, dirname, isdir

from localqt        import *
from PipelineChunks import *

from time           import strftime
from Messages       import messages


class Logger( QtCore.QObject ):

  def __init__( s, world ):

    QtCore.QObject.__init__( s )

    s.world   = world
    
    s.logfile = None
    s.buffer  = []


  def openLogFile( s, fname ):

    ## We shouldn't have a logFile still open, good practice suggests calling
    ## stopLogging() before attempting to open another logfile.

    s.close()

    assert type( fname ) is unicode  ## The filename ought to be transmitted
                                     ## internally as Unicode.

    dir = dirname( fname )

    if not isdir( dir ):

      try: 
        os.makedirs( dir )

      except ( IOError, OSError ):
        pass

    ## If logname exists, open it in append mode and let the codecs module
    ## handle encoding issues.

    try:
      s.logfile = codecs.open( fname, "a", "utf-8" )
      return True

    except IOError:
      return False


  def close( s ):

    if s.logfile:

      s.logfile.close()
      s.logfile = None


  def logOutput( s, chunks ):

    ## Don't buffer data if there is no logfile to send it to.
    if not s.logfile:
      return

    for chunk in chunks:

      if chunk.chunktype == ChunkTypes.TEXT:
        s.buffer.append( chunk.data )

      if       chunk.chunktype == chunktypes.FLOWCONTROL \
           and chunk.data == FlowControlChunk.LINEFEED:
        s.buffer.append( u"\n" )

    QtCore.QTimer.singleShot( 0, s.writeToFile )


  def writeToFile( s ):

    if s.logfile and s.buffer:

      s.logfile.write( "".join( s.buffer ) )
      s.logfile.flush()
      s.buffer = []


  def startLogging( s, filename, backlog="" ):

    ## TODO: handle toolbar / statusbar related stuff

    if s.isLogging():
      messages.warn( u"A logging file is already open, it will be closed." )

    if not s.openLogFile( filename ):
    
      messages.warn( u"Error while opening %s for log writing" % filename )
      return

    s.world.info( u"Started logging to %s" % basename( filename ) )

    if backlog:
    
      s.buffer.append( backlog )
      s.writeToFile()

    emit( s, SIGNAL( "nowLogging( bool )" ), s.isLogging() )


  def stopLogging( s ):

    ## TODO: handle toolbar / statusbar related stuff

    if s.isLogging():

      s.writeToFile()
      s.close()
      
      s.world.info( u"Logging stopped." )

    emit( s, SIGNAL( "nowLogging( bool )" ), s.isLogging() )


  def isLogging( s ):

    return s.logfile is not None


  def __del__( s ):

     ## last minute cleanup
     s.close()
