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
## ConfigPaths.py
##
## Contains the code that figures out the paths used by this program depending
## on the OS.
##

import os.path

from PlatformSpecific import platformSpecific

CONFIG_DIR  = platformSpecific.get_configuration_dir()
CONFIG_FILE = platformSpecific.get_configuration_file()

LOG_DIR     = os.path.join( CONFIG_DIR, "logs" )

if not os.path.exists( CONFIG_DIR ):

  try:
    os.makedirs( CONFIG_DIR )

  except ( IOError, OSError ):
    pass
    
