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

  def __init__( s, config ):

    QObject.__init__( s )

    ## Create the section for worlds in the configuration if it doesn't exist
    ## already.

    if not config.hasSection( config._worlds_section ):
      config.createSection( config._worlds_section )

    s.worldconfig = config.getSection( config._worlds_section )

    ## LEGACY: The following code manages the case of old configuration files
    ## with a different world section naming convention. (v0.2 and before.)

    for worldname, worldconf in list( s.worldconfig.sections.iteritems() ):

      ## Note how we duplicate the .iteritems() iterator into a list: that's
      ## because we'll be modifying some of its elements on the fly.

      if not hasattr( worldconf, "_name" ):
        worldconf._name = worldname

      s.worldconfig.renameSection( worldname, s.normalize( worldname ) )

    s.generateMappings()


  def generateMappings( s ):

    ## Provide mappings to lookup worlds based on their name and based on
    ## their (host, port) connection pair.

    s.name_mapping = dict(
                           ( s.normalize( conf._name ), conf )
                           for conf in s.worldconfig.sections.itervalues()
                         )

    s.hostport_mapping = {}

    for conf in s.worldconfig.sections.itervalues():
      s.hostport_mapping.setdefault(
                                     ( conf._host, conf._port ), []
                                   ).append( conf )


  def normalize( s, name ):

    return normalize_text( name.strip() )


  def knownWorldList( s ):

    return [ name
               for dummy, name
               in sorted (
                           ( s.normalize( conf._name ), conf._name )
                             for conf
                             in s.worldconfig.sections.itervalues()
                         )
           ]


  def newWorldConf( s, host="", port=0, ssl=False, name="" ):

    worldconf       = s.worldconfig.createAnonymousSection()

    if host: worldconf._host = host
    if port: worldconf._port = port
    if name: worldconf._name = name
    if ssl:  worldconf._ssl  = ssl

    return worldconf


  def saveWorld( s, world ):

    if world.isAnonymous():

      world.conf.saveAsSection( s.normalize( world.conf._name ) )
      s.generateMappings()

      s.worldListChanged.emit()


  def newWorld( s, conf ):

    return World( conf )


  def newAnonymousWorld( s, host="", port=0, ssl=False ):

    conf = s.newWorldConf( host, port, ssl )
    return s.newWorld( conf )


  def lookupWorldByName( s, name ):

    conf = s.name_mapping.get( s.normalize( name ) )

    if conf:
      return s.newWorld( conf )

    return None


  def lookupWorldByHostPort( s, host, port ):

    confs = s.hostport_mapping.get( ( host, port ) )

    if confs and len( confs ) == 1:

      ## One matching configuration found, and only one.
      return s.newWorld( confs[ 0 ] )

    return None

