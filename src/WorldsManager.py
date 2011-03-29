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
from Settings     import WORLDS
from Utilities    import normalize_text
from SettingsNode import SettingsNode


class WorldsManager( QObject ):

  worldListChanged = pyqtSignal()

  def __init__( self, config ):

    QObject.__init__( self )

    self.worldconfig = config[ WORLDS ]

    ## Safety measure: ensure all worlds have a valid name.
    n = 0
    for key, conf in self.worldconfig.sections.iteritems():
      if not conf._name:
        n += 1
        conf._name = u"(Unnamed %d)" % n

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
                                        ( conf._net._host, conf._net._port ), []
                                      ).append( conf )


  def normalize( self, name ):

    return normalize_text( name.strip() )


  def knownWorldList( self ):

    ## Return world names, sorted by normalized value.
    return [ name
               for _, name in sorted(
                   ( self.normalize( conf._name ), conf._name )
                   for conf in self.worldconfig.sections.itervalues()
               )
           ]


  def newWorldConf( self, host="", port=0, ssl=False, name="" ):

    worldconf = SettingsNode( self.worldconfig )

    if name: worldconf._name = name
    if host: worldconf._net._host = host
    if port: worldconf._net._port = port
    if ssl:  worldconf._net._ssl  = ssl

    return worldconf


  def saveWorld( self, world ):

    conf = world.conf
    if conf in self.worldconfig.sections.itervalues():
      ## World has already been saved, do nothing.
      return

    key = self.normalize( conf._name )
    self.worldconfig.sections[ key ] = conf

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

