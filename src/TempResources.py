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

  def __init__( self ):

    self.map      = {}
    self.tmpfiles = set()


  def get( self, fname ):

    if fname in self.map:
      return self.map[ fname ]

    tmpfname = self.new_temp_resource( fname ) or fname

    return self.map.setdefault( fname, tmpfname )


  def new_temp_resource( self, fname ):

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
    self.tmpfiles.add( tmpfname )

    return tmpfname


  def cleanup( self ):

    while self.tmpfiles:

      try:
        os.unlink( self.tmpfiles.pop() )
      except OSError:
        pass

    self.map.clear()


  def __del__( self ):

    self.cleanup()
