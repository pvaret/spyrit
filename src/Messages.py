# -*- coding: utf-8 -*-

## Copyright (c) 2007-2015 Pascal Varet <p.varet@gmail.com>
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


class Messages:

  def info( self, txt ):
    print u"INFO:", txt

  def debug( self, txt ):
    print u"DEBUG:", txt

  def warn( self, txt ):
    print u"WARN:", txt

  def error( self, txt ):
    print u"ERROR:", txt



messages = Messages()
