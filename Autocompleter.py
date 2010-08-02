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
## Autocompleter.py
##
## This is the Autocompleter class. It provides World Input widgets with the
## ability to tab-complete based on what has been fed into the World Output
## widget.
##


from localqt        import *

from PipelineChunks import *
from Utilities      import normalize_text

from os.path        import commonprefix
from collections    import deque

import re
import bisect


MAX_WORD_LIST_LENGTH = 1000


class CompletionList:

  def __init__( s, words=[] ):

    s.words = []

    ## Keep track of words, so we can remove the oldest ones from the list.
    ## Useful in order to avoid having completions 'polluted' by entries from
    ## 20 screens back that you no longer care about.

    s.wordcount = {}
    s.wordpipe  = deque()

    for word in words:
      s.addWord( word )


  def addWord( s, word ):

    key = normalize_text( word )

    s.wordpipe.appendleft( word )
    s.wordcount[ word ] = s.wordcount.setdefault( word, 0 ) + 1

    l = len( s.words )
    i = bisect.bisect_left( s.words, ( key, word ) )

    if not( i < l and s.words[ i ] == ( key, word ) ):

      ## Only add this word to the list if it's not already there.
      bisect.insort( s.words, ( key, word ), i, i )

    ## And now, cull the word list if it's grown too big.

    while len( s.words ) > MAX_WORD_LIST_LENGTH:

      oldword = s.wordpipe.pop()
      s.wordcount[ oldword ] -= 1

      if s.wordcount[ oldword ] == 0:

        i = bisect.bisect_left( s.words,
                                ( normalize_text( oldword ), oldword ) )
        del s.words[ i ]
        del s.wordcount[ oldword ]


  def lookup( s, prefix ):

    key = normalize_text( prefix )

    i = bisect.bisect_left( s.words, ( key, prefix ) )

    j = i
    k = i-1
    l = len( s.words )

    while j < l and s.words[ j ][ 0 ].startswith( key ): j += 1
    while k > 0 and s.words[ k ][ 0 ].startswith( key ): k -= 1

    return [ w[ 1 ] for w in s.words[ k+1:j ] ]




class Autocompleter:

  ## This matches all alphanumeric characters (including Unicode ones, such as
  ## 'é') plus a few punctuation signs so long as they are inside the matched
  ## word.

  wordmatch      = re.compile( "\w+[\w:`'.-]*\w+", re.U )
  startwordmatch = re.compile( "\w+[\w:`'.-]*$" ,  re.U )
  endwordmatch   = re.compile( "^[\w:`'.-]*" ,  re.U )


  def __init__( s ):

    s.completionlist = CompletionList()
    s.textedit       = None
    s.buffer         = []
    s.matchstate     = None


  def selectCurrentWord( s, tc ):

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

    tc.movePosition( QtGui.QTextCursor.EndOfLine,
                     QtGui.QTextCursor.KeepAnchor )
    line_end = unicode( tc.selectedText() )

    m = s.endwordmatch.findall( line_end )
    if m: word_after = m[ 0 ]
    else: word_after = ""

    ## Determine left half of word.

    tc.setPosition( pos )

    tc.movePosition( QtGui.QTextCursor.StartOfLine,
                     QtGui.QTextCursor.KeepAnchor )
    line_start = unicode( tc.selectedText() )

    m = s.startwordmatch.findall( line_start )
    if m: word_before = m[ 0 ]
    else: word_before = ""

    ## And select both halves.

    word = word_before + word_after

    tc.setPosition( pos - len( word_before ) )

    if len( word ) > 0:

      tc.movePosition( QtGui.QTextCursor.Right,
                       QtGui.QTextCursor.KeepAnchor,
                       len( word ) )


  def finalize( s ):

    tc = s.textedit.textCursor()

    pos = tc.position()
    tc.movePosition( QtGui.QTextCursor.EndOfLine )

    if tc.position() == pos:  ## Cursor was at end of line.
      tc.insertText( u" " )

    else:
      tc.setPosition( pos )
      tc.movePosition( QtGui.QTextCursor.Right )

    s.textedit.setTextCursor( tc )

    s.matchstate = None
    s.textedit   = None


  def complete( s, textedit ):

    s.textedit = textedit

    tc = textedit.textCursor()

    s.selectCurrentWord( tc )
    prefix = tc.selectedText()

    if prefix.isEmpty():

      s.textedit   = None
      s.matchstate = None

      return

    prefix = unicode( prefix )  ## Turn QString into Python string.

    ## Try to determine if we were previously cycling through a match list.
    ## This is not the textbook perfect way to do this; but then, the textbook
    ## perfect way involves monitoring events on the QTextEdit to see if the
    ## user did something other than autocomplete since last time, this here
    ## method is considerably less involved and, thanks to the magic of
    ## QTextCursor.isCopyOf(), quite reliable.

    currently_cycling = False

    if s.matchstate: ## If a previous ongoing completion exists...

      lastcursor, lastresult = s.matchstate

      if lastcursor.isCopyOf( textedit.textCursor() ): ## Is it still relevant?

        currently_cycling = True
        result            = lastresult

      else:  ## This is a new completion after all.
        s.matchstate = None

    if not currently_cycling:
      result = s.completionlist.lookup( prefix )

    ## Case one: no match. Do nothing.

    if len( result ) == 0:

      s.textedit   = None
      s.matchstate = None

      return

    ## All the following cases modify the textedit's content, so we apply the
    ## cursor back to the QTextEdit.

    textedit.setTextCursor( tc )

    if not currently_cycling:

      ## Case two: one match. Insert it!

      if len( result ) == 1:

        s.insertResult( result[ 0 ] )
        s.finalize()

        return

      ## Case three: several matches that all end with the same substring.
      ## Complete the prefix with that substring.

      suffixes = [ match[ len( prefix ): ] for match in result ]

      if len( set( suffixes ) ) == 1:  ## All matches have the same suffix.

        s.insertResult( prefix + suffixes.pop() )
        s.finalize()

        return

    ## Case four: several entirely distinct matches. Cycle through the list.

    result = result[ 1: ] + result[ :1 ]  ## Cycle matches.
    s.insertResult( result[ -1 ] )

    ## And save the state of the completion cycle.

    s.matchstate = ( textedit.textCursor(), result )
    s.textedit   = None

    ## And done!


  def insertResult( s, result ):

    if not s.textedit:
      return

    tc = s.textedit.textCursor()
    tc.insertText( result )
    s.textedit.setTextCursor( tc )


  def sink( s, chunk ):

    if chunk.chunktype == chunktypes.TEXT:
      s.buffer.append( chunk.data )

    elif  chunk.chunktype == chunktypes.FLOWCONTROL \
      and chunk.data      == chunk.LINEFEED:

      data     = u"".join( s.buffer )
      s.buffer = []

      for word in s.split( data ):
        s.completionlist.addWord( word )


  def split( s, line ):

    return s.wordmatch.findall( line )
