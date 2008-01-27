# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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
## WorldBaseOutputUI.py
##
## This file contains the WorldBaseOutputUI class, which is the base class
## of the world output widget, as will be inherited by the standard world ouput
## widget, but also the world output overlay that is displayed on scrollback.
##


from localqt import *


class WorldBaseOutputUI( QtGui.QTextEdit ):
 
  def __init__( s, parent ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setReadOnly( True )
    s.setUndoRedoEnabled( False )
    s.setAutoFormatting( QtGui.QTextEdit.AutoNone )
    s.setTabChangesFocus( True )
    s.viewport().setCursor( Qt.ArrowCursor )
    s.setFocusPolicy( Qt.NoFocus )

    s.setVerticalScrollBarPolicy(   Qt.ScrollBarAlwaysOff )
    s.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )

