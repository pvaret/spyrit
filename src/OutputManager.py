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


from Globals              import LEFTARROW
from FormatStack          import FormatStack
from SearchManager        import SearchManager
from QTextFormatFormatter import QTextFormatFormatter

from pipeline             import ChunkData


## This is used a lot, so define it right away.

NL = "\n"



class OutputManager:

  def __init__( self, world, textview ):

    self.world = world
    self.view_settings  = world.settings._ui._view

    self.textview = textview

    self.textcursor = QTextCursor( textview.document() )

    self.textformat = QTextCharFormat()
    self.infoformat = QTextCharFormat()

    self.textformatmanager = FormatStack( QTextFormatFormatter( self.textformat ) )
    self.infoformatmanager = FormatStack( QTextFormatFormatter( self.infoformat ) )

    self.textformatmanager.setBaseFormat( self.view_settings._font._text_format )
    self.infoformatmanager.setBaseFormat( self.view_settings._font._info_format )

    self.view_settings.onChange( "font.text_format",
                                 self.textformatmanager.setBaseFormat )
    self.view_settings.onChange( "font.info_format",
                                 self.infoformatmanager.setBaseFormat )

    self.searchmanager = SearchManager( textview, world.settings )

    self.was_connected   = False
    self.pending_newline = False

    self.refresh()
    self.setWordWrapping()

    for key in [ "font.name", "font.size", "background.color" ]:
      self.view_settings.onChange( key, self.refresh )

    self.view_settings.onChange( "wrap_column", self.setWordWrapping )

    self.textview.setSplitScrollback( self.view_settings[ "split_scroll" ] )
    self.textview.setPaging( self.view_settings[ "paging" ] )

    self.view_settings.onChange( "split_scroll", self.textview.setSplitScrollback )
    self.view_settings.onChange( "paging",       self.textview.setPaging )


  def refresh( self ):

    self.textview.setConfiguration( self.view_settings._font._name,
                                    self.view_settings._font._size,
                                    self.view_settings._background._color )


  def setWordWrapping( self ):

    self.textview.setWordWrapColumn( self.view_settings._wrap_column )


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
