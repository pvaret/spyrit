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
## PosixSpecific.py
##
## Contains the class that implements POSIX-specific elements.
##


import os.path


class PosixSpecific:

  CONFIG_DIR  = ".spyrit"
  CONFIG_FILE = "spyrit.conf"

  should_repaint_on_scroll = False
  default_font             = u"Nimbus Mono L"

  def get_homedir( s ):
    return os.path.expanduser( "~" )


  def get_configuration_dir( s ):

    home_dir = os.path.expanduser( "~" )
    return os.path.join( s.get_homedir(), s.CONFIG_DIR )


  def get_configuration_file( s ):
    return os.path.join( s.get_configuration_dir(), s.CONFIG_FILE )


  def get_sound_backends( s ):
    return [ "pygame" ]
