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
## SingleShotTimer.py
##
## Implements a simple wrapper around QTimer for the common case where we'll be
## using a recurring singleshot timer. QTimer.singleShot() is only good for
## timers used once.
##

from __future__ import absolute_import

from PyQt5.QtCore import QTimer


class SingleShotTimer( QTimer ):

  def __init__( self, slot ):

    QTimer.__init__( self )
    self.setSingleShot( True )
    self.timeout.connect( slot )
