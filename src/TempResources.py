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
## TempResources.py
##
## Contains the TempResources class, which turns Qt resources into temporary
## physical files, for those subsystems that don't understand Qt resources.
##


import os

from PyQt4.QtCore import QFile
from PyQt4.QtCore import QTemporaryFile


class TempResources:

  def __init__( s ):

    s.map      = {}
    s.tmpfiles = set()


  def get( s, fname ):

    if fname in s.map:
      return s.map[ fname ]

    tmpfname = s.new_temp_resource( fname ) or fname

    return s.map.setdefault( fname, tmpfname )


  def new_temp_resource( s, fname ):

    ## This creates the temp file if fname is a resource, but not if it
    ## doesn't exist or is a real file.

    if not QFile.exists( fname ):
      return None

    tmp = QTemporaryFile.createLocalFile( fname )

    if not tmp:
      return None

    ## Close the temporary file for now. We only want it filled with the
    ## appropriate data for later use.

    tmp.close()

    tmpfname = unicode( tmp.fileName() )
    s.tmpfiles.add( tmpfname )

    return tmpfname


  def cleanup( s ):

    while s.tmpfiles:

      try:
        os.unlink( s.tmpfiles.pop() )
      except OSError:
        pass

    s.map.clear()


  def __del__( s ):

    s.cleanup()
