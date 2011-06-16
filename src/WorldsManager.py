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
## This file holds the WorldsManager class, which manages world properties and
## looks up, creates or deletes world configuration objects.
##

from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

from World        import World
from Utilities    import normalize_text

from SpyritSettings import WORLDS


class WorldsManager( QObject ):

  worldListChanged = pyqtSignal()

  def __init__( self, settings ):

    QObject.__init__( self )

    self.worldsettings = settings[ WORLDS ]

    ## Safety measure: ensure all worlds have a valid name.
    n = 0
    for settings in self.getWorldNodes():
      if not settings._name:
        n += 1
        settings._name = u"(Unnamed %d)" % n

    self.generateMappings()


  def getWorldNodes( self ):

    return self.worldsettings.nodes.values()


  def generateMappings( self ):

    ## Provide mappings to lookup worlds based on their name and based on
    ## their (host, port) connection pair.

    self.name_mapping = dict(
                           ( self.normalize( settings._name ), settings )
                           for settings in self.getWorldNodes()
                        )

    self.hostport_mapping = {}

    for settings in self.getWorldNodes():
      self.hostport_mapping.setdefault(
                                        ( settings._net._host, settings._net._port ), []
                                      ).append( settings )


  def normalize( self, name ):

    return normalize_text( name.strip() )


  def knownWorldList( self ):

    ## Return world names, sorted by normalized value.
    return sorted( self.getWorldNodes(), key=lambda s: self.normalize( s._name ) )


  def newWorldSettings( self, host="", port=0, ssl=False, name="" ):

    ## TODO: Add createSection() to nodes that would do the right thing?
    worldsettings = self.worldsettings.proto.build( self.worldsettings, '--' )

    if name: worldsettings._name = name
    if host: worldsettings._net._host = host
    if port: worldsettings._net._port = port
    if ssl:  worldsettings._net._ssl  = ssl

    return worldsettings


  def saveWorld( self, world ):

    settings = world.settings
    if settings in self.worldsettings.sections:
      ## World has already been saved, do nothing.
      return

    ## TODO: Ensure unicity!
    key = self.normalize( settings._name )
    self.worldsettings.sections[ key ] = settings

    self.generateMappings()
    self.worldListChanged.emit()


  def newWorld( self, settings ):

    return World( settings )


  def newAnonymousWorld( self, host="", port=0, ssl=False ):

    settings = self.newWorldSettings( host, port, ssl )
    return self.newWorld( settings )


  def lookupWorldByName( self, name ):

    settings = self.name_mapping.get( self.normalize( name ) )

    if settings:
      return self.newWorld( settings )

    return None


  def lookupWorldByHostPort( self, host, port ):

    settings = self.hostport_mapping.get( ( host, port ) )

    if settings and len( settings ) == 1:

      ## One matching configuration found, and only one.
      return self.newWorld( settings[ 0 ] )

    return None

