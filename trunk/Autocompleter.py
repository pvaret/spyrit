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

import re
import bisect


MAX_WORD_LIST_LENGTH = 1000


class CompletionList:

  ## This matches all alphanumeric characters (including Unicode ones, such as
  ## 'é') plus a few punctuation signs so long as they are inside the matched
  ## word.

  wordmatch   = re.compile( "\w+[\w:`'-]*\w+", re.U )
  prefixmatch = re.compile( "\w+[\w:`'-]*$" ,  re.U )


  def __init__( s, words=[] ):

    s.words = []

    ## Keep track of words, so we can remove the oldest ones from the list.
    ## Useful in order to avoid having completions 'polluted' by entries from
    ## 20 screens back that you no longer care about.

    s.wordcount = {}
    s.wordpipe  = []

    for word in words: s.addWord( word )


  def addWord( s, word ):

    key = normalize_text( word )

    s.wordpipe.append( word )
    s.wordcount[ word ] = s.wordcount.setdefault( word, 0 ) + 1

    l = len( s.words )
    i = bisect.bisect_left( s.words, ( key, word ) )

    if not( i < l and s.words[ i ] == ( key, word ) ):

      ## Only add this word to the list if it's not already there.
      bisect.insort( s.words, ( key, word ), i, i )

    ## And now, cull the word list if it's grown too big.

    while len( s.words ) > MAX_WORD_LIST_LENGTH:

      oldword = s.wordpipe.pop( 0 )
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


  def split( s, line ):

    return s.wordmatch.findall( line )


class Autocompleter:

  def __init__( s ):

    s.completionlist = CompletionList()
    s.textedit       = None
    s.buffer         = []
    s.matchstate     = None


  def complete( s, textedit ):

    s.textedit = textedit

    tc = textedit.textCursor()

    ## TODO: Move cursor to end of word, not by Qt's standards, but by our
    ## own according to the regexes defined above. Otherwise, when completing,
    ## says, "one|-two", with | representing the cursor's position, the result
    ## will be "one-two |-two" because to Qt '-two' is a different word. Blah.

    tc.movePosition( QtGui.QTextCursor.EndOfWord )
    tc.movePosition( QtGui.QTextCursor.StartOfLine,
                     QtGui.QTextCursor.KeepAnchor )
    line = unicode( tc.selectedText() )
    m = s.completionlist.prefixmatch.findall( line )

    if not m:
      return

    prefix = m[ 0 ]

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

    if not currently_cycling:
      result = s.completionlist.lookup( prefix )

    ## Case one: no match. Do nothing.

    if len( result ) == 0:
      s.textedit = None
      return

    ## All the following cases modify the textedit's content, so we apply the
    ## cursor back to the QTextEdit.

    tc = textedit.textCursor()
    tc.movePosition( QtGui.QTextCursor.EndOfWord )
    tc.movePosition( QtGui.QTextCursor.Left,
                     QtGui.QTextCursor.KeepAnchor,
                     len( prefix ) )
    textedit.setTextCursor( tc )

    if not currently_cycling:

      ## Case two: one match. Insert it!

      if len( result ) == 1:

        s.insertResult( result[ 0 ] + u" " )
        s.matchstate = None

        return

      ## Case three: several matches that all end with the same substring.
      ## Complete the prefix with that substring.

      suffixes = [ match[ len( prefix ): ] for match in result ]

      if len( set( suffixes ) ) == 1:  ## All matches have the same suffix.

        s.insertResult( prefix + suffixes.pop() + u" " )
        s.matchstate = None

        return

    ## Case four: several entirely distinct matches. Cycle through the list.

    result = result[ 1: ] + result[ :1 ]  ## Cycle matches.
    s.insertResult( result[ -1 ] )

    ## And save the state of the completion cycle.

    s.matchstate = ( textedit.textCursor(), result )

    ## And done!
    

  def insertResult( s, result ):

    if not s.textedit:
      return

    tc = s.textedit.textCursor()
    tc.insertText( result )
    s.textedit.setTextCursor( tc )

    s.textedit = None


  def sink( s, chunks ):

    for chunk in chunks:

      if chunk.chunktype == chunktypes.TEXT:
        s.buffer.append( chunk.data )

      if     chunk.chunktype == chunktypes.FLOWCONTROL \
         and chunk.data      == chunk.LINEFEED:
        
        data     = "".join( s.buffer )
        s.buffer = []

        for word in s.completionlist.split( data ):
          s.completionlist.addWord( word )
