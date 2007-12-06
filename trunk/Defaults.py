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
## Defaults.py
##
## Contains the default configuration items.
##

from localqt import *


_defaults = dict(

  app_name            = "Spyrit",
  app_version         = "0.3pre",
  mainwindow_min_size = ( 320, 200 ),
  mainwindow_pos      = None,
  worlds_section      = "Worlds",

  ssl                 = False,  ## By default, no SSL on sockets.

  show_splashscreen = False,
  mainwindow_size   = ( 800, 600 ),

  output_font_name  = "Courier",
  output_font_size  = 0,  ## Nothing, system default will be used.
  output_font_color = "#c0c0c0",  ## light grey

  bold_as_highlight = True,

  info_font_color   = "#606060",  ## dark grey

  input_font_name  = "",  ## Nothing, system default will be used.
  input_font_size  = 0,   ## Nothing, system default will be used.
  input_font_color = "",  ## Nothing, system default will be used.

  output_background_color = "#000000",  ## black
  input_background_color  = "#ffffff",  ## white

  splitter_sizes = [ 1000, 100, 100 ],

  input_command_char = "/",

  alert_on_activity  = True,

)


from ConfigBasket import ConfigBasket

defaults = ConfigBasket()
defaults.updateFromDict( _defaults )
