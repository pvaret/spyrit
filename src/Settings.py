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
## Settings.py
##
## Holds the core settings object, which knows the details of our settings.
##

from ConfigBasket import ConfigBasket


class Settings:

  def __init__( self, schema ):

    self.schema = schema
    self.basket = ConfigBasket()


  def save( self ):
    pass

  def toDict( self ):
    pass

  def fromDict( self ):
    pass
