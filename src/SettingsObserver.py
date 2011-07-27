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
## SettingsObserver.py
##
## This file holds SettingsObserver, a helper class that monitors changes in a
## Configuration object and calls the appropriate callback when that happens.
##



class SettingsObserver:

  def __init__( self, settings ):

    self.settings = settings


  def addCallback( self, keys, callback ):

    if type( keys ) not in ( list, tuple, set ):
      keys = [ keys ]

    for key in keys:
      self.settings.get( key ).notifier.add( callback )

    return self  ## Return self, so as to make it possible to chain calls.
