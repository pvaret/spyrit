# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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
## QSoundBackend.py
##
## Implements the QSound-based sound backend. It should work on Windows and
## Mac OS X by default, but probably not on Linux, as it relies on a
## particular sound server that isn't commonly installed.
##


try:
  from PyQt5.QtMultimedia import QSound

except ImportError:
  ## QtMultimedia is optional and may not be installed.
  QSound = None


class QSoundBackend:

  name = u"Native (Qt)"

  def isAvailable( self ):

    return QSound is not None and QSound.isAvailable()


  def play( self, soundfile ):

    QSound.play( soundfile )
