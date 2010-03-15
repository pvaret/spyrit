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
## OutputManager.py
##
## This file contains the OutputManager class, which is in charge of content
## management in the output UI: text insertion, formatting, search, etc.
##


from localqt import *

from PipelineChunks import *
from SearchManager  import SearchManager
from FormatManager  import FormatManager
from ConfigObserver import ConfigObserver

from Singletons import singletons


## This is used a lot, so define it right away.

NL = "\n"


## Special Unicode characters.

LEFTARROW = unichr( 0x2192 )


class OutputManager:

  def __init__( s, world, textview ):

    s.world = world
    s.conf  = world.conf

    s.textview = textview

    s.textcursor = QtGui.QTextCursor( textview.document() )

    s.observer = ConfigObserver( s.conf )

    s.textformat = QtGui.QTextCharFormat()
    s.infoformat = QtGui.QTextCharFormat()

    s.textformatmanager = FormatManager( s.textformat )
    s.infoformatmanager = FormatManager( s.infoformat )

    s.textformatmanager.setBaseFormat( s.conf[ "output_format" ] )
    s.infoformatmanager.setBaseFormat( s.conf[ "info_format" ] )

    s.observer.addCallback( "output_format",
                            s.textformatmanager.setBaseFormat )
    s.observer.addCallback( "info_format",
                            s.infoformatmanager.setBaseFormat )

    s.searchmanager = SearchManager( textview, s.conf )

    s.was_connected   = False
    s.pending_newline = False

    s.refresh()

    s.observer.addCallback( [ "output_font_name",
                              "output_font_size",
                              "output_background_color" ],
                            s.refresh )

    s.textview.setSplitScrollback( s.conf[ "split_scrollback" ] )
    s.textview.setPaging(          s.conf[ "paging" ] )

    s.observer.addCallback( "split_scrollback", s.textview.setSplitScrollback )
    s.observer.addCallback( "paging",           s.textview.setPaging )


  def refresh( s ):

    s.textview.setConfiguration( s.conf._output_font_name,
                                 s.conf._output_font_size,
                                 s.conf._output_background_color )


  def findInHistory( s, string ):

    return s.searchmanager.find( string )


  def processChunks( s, chunks ):
    
    s.textcursor.beginEditBlock()

    for chunk in chunks:

      if   chunk.chunktype == chunktypes.TEXT:
        s.insertText( chunk.data )

      elif chunk.chunktype == chunktypes.FLOWCONTROL:
        s.processFlowControlChunk( chunk.data )

      elif chunk.chunktype == chunktypes.ANSI:
        s.textformatmanager.applyAnsiFormat( chunk.data )

      elif chunk.chunktype == chunktypes.HIGHLIGHT:
        s.textformatmanager.applyHighlightFormat( chunk.data )

      elif chunk.chunktype == chunktypes.NETWORK:
        s.processNetworkChunk( chunk.data )

    s.textcursor.endEditBlock()

    if s.conf._alert_on_activity:
      qApp().alert( s.textview.window() )


  def processFlowControlChunk( s, event ):

    if event == FlowControlChunk.LINEFEED:
      s.insertNewLine()


  def processNetworkChunk( s, event ):

    if   event == NetworkChunk.CONNECTING:
      s.insertInfoText( u"Connecting..." )

    elif event == NetworkChunk.CONNECTED:

      if not s.was_connected:
        s.insertInfoText( u"Connected!" )
        s.was_connected = True

    elif event == NetworkChunk.ENCRYPTED:
      s.insertInfoText( u"SSL encryption started." )

    elif event == NetworkChunk.DISCONNECTED:

      if s.was_connected:
        s.insertInfoText( u"Connection closed." )
        s.was_connected = False

    elif event == NetworkChunk.RESOLVING:
      s.insertInfoText( u"Resolving %s ..." % s.world.host() )


    elif event == NetworkChunk.CONNECTIONREFUSED:
      s.insertInfoText( u"Connection refused." )

    elif event == NetworkChunk.HOSTNOTFOUND:
      s.insertInfoText( u"Host not found." )

    elif event == NetworkChunk.TIMEOUT:
      s.insertInfoText( u"Network timeout." )

    elif event == NetworkChunk.OTHERERROR:
      s.insertInfoText( u"Network error." )


  def insertNewLine( s ):

    if s.pending_newline:
      s.textcursor.insertText( NL, s.textformat )

    s.pending_newline = True


  def insertText( s, text ):

    if s.pending_newline:

      s.textcursor.insertText( NL, s.textformat )
      s.pending_newline = False

    s.textcursor.insertText( text, s.textformat )
    

  def insertInfoText( s, text ):

    if s.textcursor.columnNumber() > 0:
      s.textcursor.insertText( NL, s.infoformat )

    s.textcursor.insertText( LEFTARROW + " " + text, s.infoformat )
    s.pending_newline = True  ## There is always a new line after info text.


  def __del__( s ):

    s.world          = None
    s.conf           = None
    s.textcursor     = None
    s.charformat     = None
    s.infocharformat = None
    s.observer       = None
    s.searchmanager  = None
