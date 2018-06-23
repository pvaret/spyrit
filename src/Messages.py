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
## Messages.py
##
## Defines a Messages class that can be used to keep track of errors, warnings,
## etc, that take place inside the program.
## By default, the class only prints to stdout.
##

from __future__ import print_function


class Messages:

  def info( self, txt ):
    try:
      print( u"INFO:", txt )
    except IOError:
      pass

  def debug( self, txt ):
    try:
      print( u"DEBUG:", txt )
    except IOError:
      pass

  def warn( self, txt ):
    try:
      print( u"WARN:", txt )
    except IOError:
      pass

  def error( self, txt ):
    try:
      print( u"ERROR:", txt )
    except IOError:
      pass



messages = Messages()
