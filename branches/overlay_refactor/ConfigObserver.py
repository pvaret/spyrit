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
## ConfigObserver.py
##
## This file holds ConfigObserver, a helper class that monitors changes in a
## Configuration object and calls the appropriate callback when that happens.
##


class ConfigObserver:

  def __init__( s, conf ):

    s.callbacks = {}
    conf.registerNotifier( s.notify )


  def notify( s, key ):

    for callback in s.callbacks.get( key, [] ): callback()


  def addCallback( s, keys, callback ):

    if type( keys ) not in ( type( [] ), type( () ) ): keys = [ keys ]

    for key in keys:
      s.callbacks.setdefault( key, [] ).append( callback )
