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
## SearchManager.py
##
## This file implements the SearchManager class, a helper that handles all
## aspects of searching the contents of a QTextEdit such as WorldOutputUI.
##

from localqt           import *

class SearchManager:

  def __init__( s, textedit, conf ):

    s.textedit = textedit
    s.conf     = conf

    s.cursor          = None
    s.previous_search = None


  def find( s, string=None ):

    ## An empty search string means repeating the last search.

    if not string:
      string = s.previous_search

    ## Unless the last search was empty, in which case we bail out.

    if not string:
      return False

    ## Reset the search cursor if this is a new search.

    if string != s.previous_search:
      s.cursor = None

    cursor   = s.cursor
    textedit = s.textedit
    document = textedit.document()

    s.previous_search = string

    ## Create new cursor at end of document if this is a new search.

    if not cursor:
      cursor = QtGui.QTextCursor( document )
      cursor.movePosition( QtGui.QTextCursor.End )

    cursor = document.find( string, cursor, QtGui.QTextDocument.FindBackward )

    if cursor.isNull():  ## String was not found!

      ## Clear selection by setting an empty cursor, and scroll back to bottom
      ## of window.

      cursor = QtGui.QTextCursor( document )
      textedit.setTextCursor( cursor )
      textedit.moveScrollbarToBottom()

      s.cursor = None

      return False

    else:

      textedit.setTextCursor( cursor )
      textedit.ensureCursorVisible()

      s.cursor = cursor

      return True


  def __del__( s ):

    s.conf     = None
    s.cursor   = None
    s.textedit = None
