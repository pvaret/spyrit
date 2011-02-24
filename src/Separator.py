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
## Separator.py
##
## This file contains the Separator widget, which draws a horizontal line
## and does nothing else.
##


from PyQt4.QtGui import QFrame


class Separator( QFrame ):

  def __init__( s, parent=None ):

    QFrame.__init__( s, parent )

    s.setLineWidth( 1 );
    s.setMidLineWidth( 0 );
    s.setFrameShape ( QFrame.HLine )
    s.setFrameShadow( QFrame.Sunken )
    s.setMinimumSize( 0, 2 );
