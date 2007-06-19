##
## InputHistory.py
##
## Holds the InputHistory class, which manages the history of what the user
## typed in the input widget.
##

from localqt import *


class InputHistory:

  def __init__( s, inputwidget, maxlength=0 ):

    s.inputwidget = inputwidget
    s.maxlength   = maxlength
    s.history     = []
    s.cursor      = -1
    s.currenttext = ""


  def historyUp( s ):

    if len ( s.history ) ==  0 or s.cursor >= len( s.history ) - 1:
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
    if s.maxlength and len( s.history ) > s.maxlength:
      s.history.pop()
