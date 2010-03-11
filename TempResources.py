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
## TempResources.py
##
## Contains the TempResources class, which turns Qt resources into temporary
## physical files, for those subsystems that don't understand Qt resources.
##


from localqt import *

class TempResources:

  def __init__( s ):

    s.tempfiles = {}


  def get( s, fname ):

    tmpfname = s.tempfiles.setdefault( fname, s.new_temp_resource( fname ) )

    return tmpfname or fname


  def new_temp_resource( s, fname ):

    data = QtCore.QFile( fname )

    if not data.exists():
      return None

    ## XXX Implement tmpfile generation and cleanup.
