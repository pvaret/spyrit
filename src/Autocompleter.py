# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## Autocompleter.py
##
## This is the Autocompleter class. It provides World Input widgets with the
## ability to tab-complete based on what has been fed into the World Output
## widget.
##


import re
import bisect

from collections import deque

from PyQt5.QtGui import QTextCursor

from pipeline.ChunkData import ChunkType
from pipeline.ChunkData import FlowControl
from Utilities          import normalize_text


MAX_WORD_LIST_LENGTH = 1000


class CompletionList:

  def __init__( self, words=[] ):

    self.words = []

    ## Keep track of words, so we can remove the oldest ones from the list.
    ## Useful in order to avoid having completions 'polluted' by entries from
    ## 20 screens back that you no longer care about.

    self.wordcount = {}
    self.wordpipe  = deque()

    for word in words:
      self.addWord( word )


  def addWord( self, word ):

    key = normalize_text( word )

    self.wordpipe.appendleft( word )
    self.wordcount[ word ] = self.wordcount.setdefault( word, 0 ) + 1

    l = len( self.words )
    i = bisect.bisect_left( self.words, ( key, word ) )

    if not( i < l and self.words[ i ] == ( key, word ) ):

      ## Only add this word to the list if it's not already there.
      bisect.insort( self.words, ( key, word ), i, i )

    ## And now, cull the word list if it's grown too big.

    while len( self.words ) > MAX_WORD_LIST_LENGTH:

      oldword = self.wordpipe.pop()
      self.wordcount[ oldword ] -= 1

      if self.wordcount[ oldword ] == 0:

        i = bisect.bisect_left( self.words,
                                ( normalize_text( oldword ), oldword ) )
        del self.words[ i ]
        del self.wordcount[ oldword ]


  def lookup( self, prefix ):

    key = normalize_text( prefix )

    i = bisect.bisect_left( self.words, ( key, prefix ) )

    j = i
    k = i-1
    l = len( self.words )

    while j < l and self.words[ j ][ 0 ].startswith( key ): j += 1
    while k > 0 and self.words[ k ][ 0 ].startswith( key ): k -= 1

    return [ w[ 1 ] for w in self.words[ k+1:j ] ]




class Autocompleter:

  ## This matches all alphanumeric characters (including Unicode ones, such as
  ## 'é') plus a few punctuation signs so long as they are inside the matched
  ## word.

  wordmatch      = re.compile( "\w+[\w:`'.-]*\w+", re.U )
  startwordmatch = re.compile( "\w+[\w:`'.-]*$" ,  re.U )
  endwordmatch   = re.compile( "^[\w:`'.-]*" ,  re.U )


  def __init__( self ):

    self.completionlist = CompletionList()
    self.textedit       = None
    self.buffer         = []
    self.matchstate     = None


  def selectCurrentWord( self, tc ):

    ## Alright. Our problem here is that we'd like to select the current word,
    ## but Qt's idea of what makes up a word is, it seems, inconsistent across
    ## Qt versions, and also incompatible with what Spyrit itself considers a
    ## word.
    ## For instance, in the name "O'hara", Qt considers "O" and "hara" to be
    ## separate words, which doesn't work at all for us.
    ## Hence, this method, which essentially does a
    ## QTextCursor.select( WordUnderCursor ), but, our way. Phew.

    tc.clearSelection()

    pos = tc.position()

    ## Determine right half of word.

    tc.movePosition( QTextCursor.EndOfLine,
                     QTextCursor.KeepAnchor )
    line_end = str( tc.selectedText() )

    m = self.endwordmatch.findall( line_end )
    if m: word_after = m[ 0 ]
    else: word_after = ""

    ## Determine left half of word.

    tc.setPosition( pos )

    tc.movePosition( QTextCursor.StartOfLine,
                     QTextCursor.KeepAnchor )
    line_start = str( tc.selectedText() )

    m = self.startwordmatch.findall( line_start )
    if m: word_before = m[ 0 ]
    else: word_before = ""

    ## And select both halves.

    word = word_before + word_after

    tc.setPosition( pos - len( word_before ) )

    if len( word ) > 0:

      tc.movePosition( QTextCursor.Right,
                       QTextCursor.KeepAnchor,
                       len( word ) )


  def finalize( self ):

    tc = self.textedit.textCursor()

    pos = tc.position()
    tc.movePosition( QTextCursor.EndOfLine )

    if tc.position() == pos:  ## Cursor was at end of line.
      tc.insertText( u" " )

    else:
      tc.setPosition( pos )
      tc.movePosition( QTextCursor.Right )

    self.textedit.setTextCursor( tc )

    self.matchstate = None
    self.textedit   = None


  def complete( self, textedit ):

    self.textedit = textedit

    tc = textedit.textCursor()

    self.selectCurrentWord( tc )
    prefix = tc.selectedText()

    if not prefix:

      self.textedit   = None
      self.matchstate = None

      return

    ## Try to determine if we were previously cycling through a match list.
    ## This is not the textbook perfect way to do this; but then, the textbook
    ## perfect way involves monitoring events on the QTextEdit to see if the
    ## user did something other than autocomplete since last time, this here
    ## method is considerably less involved and, thanks to the magic of
    ## QTextCursor.isCopyOf(), quite reliable.

    currently_cycling = False

    if self.matchstate: ## If a previous ongoing completion exists...

      lastcursor, lastresult = self.matchstate

      if lastcursor.isCopyOf( textedit.textCursor() ): ## Is it still relevant?

        currently_cycling = True
        result            = lastresult

      else:  ## This is a new completion after all.
        self.matchstate = None

    if not currently_cycling:
      result = self.completionlist.lookup( prefix )

    ## Case one: no match. Do nothing.

    if len( result ) == 0:

      self.textedit   = None
      self.matchstate = None

      return

    ## All the following cases modify the textedit's content, so we apply the
    ## cursor back to the QTextEdit.

    textedit.setTextCursor( tc )

    if not currently_cycling:

      ## Case two: one match. Insert it!

      if len( result ) == 1:

        self.insertResult( result[ 0 ] )
        self.finalize()

        return

      ## Case three: several matches that all end with the same substring.
      ## Complete the prefix with that substring.

      suffixes = [ match[ len( prefix ): ] for match in result ]

      if len( set( suffixes ) ) == 1:  ## All matches have the same suffix.

        self.insertResult( prefix + suffixes.pop() )
        self.finalize()

        return

    ## Case four: several entirely distinct matches. Cycle through the list.

    result = result[ 1: ] + result[ :1 ]  ## Cycle matches.
    self.insertResult( result[ -1 ] )

    ## And save the state of the completion cycle.

    self.matchstate = ( textedit.textCursor(), result )
    self.textedit   = None

    ## And done!


  def insertResult( self, result ):

    if not self.textedit:
      return

    tc = self.textedit.textCursor()
    tc.insertText( result )
    self.textedit.setTextCursor( tc )


  def sink( self, chunk ):

    chunk_type, payload = chunk

    if chunk_type == ChunkType.TEXT:
      self.buffer.append( payload )

    elif chunk == ( ChunkType.FLOWCONTROL, FlowControl.LINEFEED ):

      data     = u"".join( self.buffer )
      self.buffer = []

      for word in self.split( data ):
        self.completionlist.addWord( word )


  def split( self, line ):

    return self.wordmatch.findall( line )
