# -*- coding: utf-8 -*-

## Copyright (c) 2007-2015 Pascal Varet <p.varet@gmail.com>
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



class WorldsSettings:
  """
  This class encapsulates the deep knowledge about settings objects that
  WorldsManager requires.
  """

  def __init__( self, settings ):

    self.settings = settings[ WORLDS ]


  def getAllWorldSettings( self ):

    return self.settings.nodes.values()


  def newWorldSettings( self ):

    ## TODO: Add createSection() to nodes that would do the right thing?
    return self.settings.proto.build( self.settings, '*' )


  def saveWorldSettings( self, key, settings ):

    if settings in self.getAllWorldSettings():
      ## World has already been saved, do nothing.
      return

    self.settings.nodes[ key ] = settings



class WorldsManager( QObject ):

  worldListChanged = pyqtSignal()

  def __init__( self, settings ):

    QObject.__init__( self )

    self.ws = WorldsSettings( settings )

    ## Safety measure: ensure all worlds have a valid name.
    n = 0

    for settings in self.ws.getAllWorldSettings():

      if not settings._name:
        n += 1
        settings._name = u"(Unnamed %d)" % n

    self.generateMappings()


  def generateMappings( self ):

    ## Provide mappings to lookup worlds based on their name and based on
    ## their (host, port) connection pair.

    self.name_mapping = dict(
                           ( self.normalize( settings._name ), settings )
                           for settings in self.ws.getAllWorldSettings()
                        )

    self.hostport_mapping = {}

    for settings in self.ws.getAllWorldSettings():
      self.hostport_mapping.setdefault(
                                        ( settings._net._host, settings._net._port ), []
                                      ).append( settings )


  def normalize( self, name ):

    return normalize_text( name.strip() )


  def worldList( self ):

    ## Return world names, sorted by normalized value.
    worlds = ( world._name for world in self.ws.getAllWorldSettings() )
    return sorted( worlds, key=lambda s: self.normalize( s ) )


  def newWorldSettings( self, host="", port=0, ssl=False, name="" ):

    wsettings = self.ws.newWorldSettings()

    if name: wsettings._name      = name
    if host: wsettings._net._host = host
    if port: wsettings._net._port = port
    if ssl:  wsettings._net._ssl  = ssl

    return wsettings


  def saveWorld( self, world ):

    settings = world.settings
    key = self.normalize( settings._name )  ## TODO: Ensure unicity!

    self.ws.saveWorldSettings( key, settings )

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
