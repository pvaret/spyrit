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
## InputHistory.py
##
## Holds the InputHistory class, which manages the history of what the user
## typed in the input widget.
##

from localqt import *


class InputHistory:

  def __init__( s, inputwidget ):

    s.inputwidget = inputwidget
    s.cursor      = -1
    s.currenttext = ""

    conf = inputwidget.world.conf

    if conf._save_input_history:

      try:
        count = int( conf._save_input_history )

      except ValueError:
        count = 0

      s.history = conf._input_history[ :count ]

    else:
      s.history = []


  def historyUp( s ):

    if len ( s.history ) == 0 or s.cursor >= len( s.history ) - 1:
      return

    s.cursor += 1

    if s.cursor == 0:
      s.currenttext = s.inputwidget.toPlainText()

    s.inputwidget.setPlainText( s.history[ s.cursor ] )
    s.inputwidget.moveCursor( QtGui.QTextCursor.End )


  def historyDown( s ):

    if s.cursor < 0:
      return

    s.cursor -= 1

    if s.cursor == -1:
      s.inputwidget.setPlainText( s.currenttext )

    else:
      s.inputwidget.setPlainText( s.history[ s.cursor ] )

    s.inputwidget.moveCursor( QtGui.QTextCursor.End )


  def update( s, text ):

    s.currenttext = ""
    s.cursor      = -1

    s.history.insert( 0, text )

    conf = s.inputwidget.world.conf

    maxlength = conf._max_history_length

    if maxlength and len( s.history ) > maxlength:
      s.history.pop()

    count = int( conf._save_input_history )
    if count: conf._input_history = s.history[ :count ]
