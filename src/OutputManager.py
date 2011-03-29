# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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


from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QTextCharFormat


from SearchManager        import SearchManager
from FormatStack          import FormatStack
from QTextFormatFormatter import QTextFormatFormatter
from ConfigObserver       import ConfigObserver
from Globals              import LEFTARROW

from pipeline             import ChunkData


## This is used a lot, so define it right away.

NL = "\n"



class OutputManager:

  def __init__( self, world, textview ):

    self.world = world
    self.conf  = world.conf

    self.textview = textview

    self.textcursor = QTextCursor( textview.document() )

    view_conf = self.conf._ui._view
    text_conf = view_conf._font
    self.obs1 = ConfigObserver( text_conf )
    self.obs2 = ConfigObserver( view_conf._background )
    self.obs3 = ConfigObserver( view_conf )

    self.textformat = QTextCharFormat()
    self.infoformat = QTextCharFormat()

    self.textformatmanager = FormatStack( QTextFormatFormatter( self.textformat ) )
    self.infoformatmanager = FormatStack( QTextFormatFormatter( self.infoformat ) )

    self.textformatmanager.setBaseFormat( text_conf[ "text_format" ] )
    self.infoformatmanager.setBaseFormat( text_conf[ "info_format" ] )

    self.obs1.addCallback( "text_format", self.textformatmanager.setBaseFormat )
    self.obs1.addCallback( "info_format", self.infoformatmanager.setBaseFormat )

    self.searchmanager = SearchManager( textview, self.conf )

    self.was_connected   = False
    self.pending_newline = False

    self.refresh()

    self.obs1.addCallback( [ "name", "size" ], self.refresh )
    self.obs2.addCallback( "color", self.refresh )

    self.textview.setSplitScrollback( view_conf[ "split_scroll" ] )
    self.textview.setPaging(          view_conf[ "paging" ] )

    self.obs3.addCallback( "split_scroll", self.textview.setSplitScrollback )
    self.obs3.addCallback( "paging",       self.textview.setPaging )


  def refresh( self ):

    self.textview.setConfiguration( self.conf._ui._view._font._name,
                                    self.conf._ui._view._font._size,
                                    self.conf._ui._view._background._color )


  def findInHistory( self, string ):

    return self.searchmanager.find( string )


  def processChunk( self, chunk ):

    chunk_type, payload = chunk

    if chunk_type == ChunkData.TEXT:
      self.insertText( payload )

    elif chunk_type == ChunkData.FLOWCONTROL:
      self.processFlowControlChunk( payload )

    elif chunk_type == ChunkData.NETWORK:
      self.processNetworkChunk( payload )


  def processFlowControlChunk( self, event ):

    if event == ChunkData.LINEFEED:
      self.insertNewLine()


  def processNetworkChunk( self, event ):

    if   event == ChunkData.CONNECTING:
      self.insertInfoText( u"Connecting..." )

    elif event == ChunkData.CONNECTED:

      if not self.was_connected:
        self.insertInfoText( u"Connected!" )
        self.was_connected = True

    elif event == ChunkData.ENCRYPTED:
      self.insertInfoText( u"SSL encryption started." )

    elif event == ChunkData.DISCONNECTED:

      if self.was_connected:
        self.insertInfoText( u"Connection closed." )
        self.was_connected = False

    elif event == ChunkData.RESOLVING:
      self.insertInfoText( u"Resolving %s ..." % self.world.host() )


    elif event == ChunkData.CONNECTIONREFUSED:
      self.insertInfoText( u"Connection refused." )

    elif event == ChunkData.HOSTNOTFOUND:
      self.insertInfoText( u"Host not found." )

    elif event == ChunkData.TIMEOUT:
      self.insertInfoText( u"Network timeout." )

    elif event == ChunkData.OTHERERROR:
      self.insertInfoText( u"Network error." )


  def insertNewLine( self ):

    if self.pending_newline:
      self.textcursor.insertText( NL, self.textformat )

    self.pending_newline = True


  def insertText( self, text ):

    if self.pending_newline:

      self.textcursor.insertText( NL, self.textformat )
      self.pending_newline = False

    self.textcursor.insertText( text, self.textformat )


  def insertInfoText( self, text ):

    if self.textcursor.columnNumber() > 0:
      self.textcursor.insertText( NL, self.infoformat )

    text = text.rstrip()

    self.textcursor.insertText( LEFTARROW + " " + text, self.infoformat )
    self.pending_newline = True  ## There is always a new line after info text.


  def __del__( self ):

    self.world          = None
    self.conf           = None
    self.textcursor     = None
    self.charformat     = None
    self.infocharformat = None
    self.obs1           = None
    self.obs2           = None
    self.obs3           = None
    self.searchmanager  = None
