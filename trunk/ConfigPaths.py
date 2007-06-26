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
## ConfigPaths.py
##
## Contains the code that figures out the paths used by this program depending
## on the OS.
##


import os

if os.name in ( 'posix', 'mac' ):

  HOME_DIR    = os.path.expanduser( "~" )
  CONFIG_DIR  = os.path.join( HOME_DIR,   ".spyrit" )
  CONFIG_FILE = os.path.join( CONFIG_DIR, "spyrit.conf" )

  if not os.path.exists( CONFIG_DIR ):

    try:
      os.mkdir( CONFIG_DIR )

    except IOError:
      pass
    

#elif os.name in ( 'nt,' ):
#  pass

else:
  raise NotImplementedError( "This program doesn't support your OS yet. Sorry!" )
