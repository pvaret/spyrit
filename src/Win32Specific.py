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
## Win32Specific.py
##
## Contains the class that implements Windows-specific elements.
##


import os.path
import winpaths


class Win32Specific:

  CONFIG_DIR  = "Spyrit"
  CONFIG_FILE = "Spyrit.ini"

  should_repaint_on_scroll = False
  default_font             = u"Courier New"

  def get_homedir( self ):
    return winpaths.get_homedir()

  def get_configuration_dir( self ):
    return os.path.join( winpaths.get_appdata(), self.CONFIG_DIR )

  def get_configuration_file( self ):
    return os.path.join( self.get_configuration_dir(), self.CONFIG_FILE )

  def get_sound_backends( self ):
    return [ "qsound" ]
