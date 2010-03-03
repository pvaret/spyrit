# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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
## FormatData.py
##
## This file describes various bits of formatting related data.
##


from localqt import *


class FORMAT_PROPERTIES:

  COLOR     = QtGui.QTextFormat.ForegroundBrush
  BOLD      = QtGui.QTextFormat.FontWeight
  ITALIC    = QtGui.QTextFormat.FontItalic
  UNDERLINE = QtGui.QTextFormat.TextUnderlineStyle


class ANSI_COLORS:

  ## Dark colors:

  black     = "#000000"
  red       = "#800000"
  green     = "#008000"
  yellow    = "#808000"
  blue      = "#000080"
  magenta   = "#800080"
  cyan      = "#008080"
  lightgray = "#c0c0c0"

  ## Light colors:

  darkgray  = "#808080"
  red_h     = "#ff0000"
  green_h   = "#00ff00"
  yellow_h  = "#ffff00"
  blue_h    = "#0000ff"
  magenta_h = "#ff00ff"
  cyan_h    = "#00ffff"
  white     = "#ffffff"
