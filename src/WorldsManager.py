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

from World      import World
from Utilities  import normalize_text


class WorldsManager( QObject ):

  worldListChanged = pyqtSignal()

  def __init__( self, config ):

    QObject.__init__( self )

    ## Create the section for worlds in the configuration if it doesn't exist
    ## already.

    if not config.hasSection( config._worlds_section ):
      config.createSection( config._worlds_section )

    self.worldconfig = config.getSection( config._worlds_section )

    ## LEGACY: The following code manages the case of old configuration files
    ## with a different world section naming convention. (v0.2 and before.)

    for worldname, worldconf in list( self.worldconfig.sections.iteritems() ):

      ## Note how we duplicate the .iteritems() iterator into a list: that's
      ## because we'll be modifying some of its elements on the fly.

      if not hasattr( worldconf, "_name" ):
        worldconf._name = worldname

      self.worldconfig.renameSection( worldname, self.normalize( worldname ) )

    self.generateMappings()


  def generateMappings( self ):

    ## Provide mappings to lookup worlds based on their name and based on
    ## their (host, port) connection pair.

    self.name_mapping = dict(
                           ( self.normalize( conf._name ), conf )
                           for conf in self.worldconfig.sections.itervalues()
                         )

    self.hostport_mapping = {}

    for conf in self.worldconfig.sections.itervalues():
      self.hostport_mapping.setdefault(
                                        ( conf._host, conf._port ), []
                                      ).append( conf )


  def normalize( self, name ):

    return normalize_text( name.strip() )


  def knownWorldList( self ):

    return [ name
               for dummy, name
               in sorted (
                           ( self.normalize( conf._name ), conf._name )
                             for conf
                             in self.worldconfig.sections.itervalues()
                         )
           ]


  def newWorldConf( self, host="", port=0, ssl=False, name="" ):

    worldconf = self.worldconfig.createAnonymousSection()

    if host: worldconf._host = host
    if port: worldconf._port = port
    if name: worldconf._name = name
    if ssl:  worldconf._ssl  = ssl

    return worldconf


  def saveWorld( self, world ):

    if world.isAnonymous():

      world.conf.saveAsSection( self.normalize( world.conf._name ) )
      self.generateMappings()

      self.worldListChanged.emit()


  def newWorld( self, conf ):

    return World( conf )


  def newAnonymousWorld( self, host="", port=0, ssl=False ):

    conf = self.newWorldConf( host, port, ssl )
    return self.newWorld( conf )


  def lookupWorldByName( self, name ):

    conf = self.name_mapping.get( self.normalize( name ) )

    if conf:
      return self.newWorld( conf )

    return None


  def lookupWorldByHostPort( self, host, port ):

    confs = self.hostport_mapping.get( ( host, port ) )

    if confs and len( confs ) == 1:

      ## One matching configuration found, and only one.
      return self.newWorld( confs[ 0 ] )

    return None

