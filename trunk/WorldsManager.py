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
## This file holds the WorldsManager class, which manages world properties and
## looks up, creates or deletes world configuration objects.
##

from localqt import *

from World      import World
from Singletons import singletons
from Utilities  import case_insensitive_cmp, remove_accents


## TODO: Have WorldsManager emit signal when world list changed.

class WorldsManager( QtCore.QObject ):
  
  def __init__( s ):
    
    QtCore.QObject.__init__( s )

    ## Create the section for worlds in the configuration if it doesn't exist
    ## already.

    config = singletons.config 

    if not config.hasDomain( config._worlds_section ):
      config.createDomain( config._worlds_section )
      
    s.worldconfig = config.getDomain( config._worlds_section )

    ## LEGACY: The following code manages the case of old configuration files
    ## with a different world section naming convention. (v0.2 and before.)

    for worldname, worldconf in list( s.worldconfig.domains.iteritems() ):

      ## Note how we duplicate the .iteritems() iterator into a list: that's
      ## because we'll be modifying some of its elements on the fly.

      if not hasattr( worldconf, "_name" ):
        worldconf._name = worldname

      s.worldconfig.renameDomain( worldname, s.normalize( worldname ) )
        
    ## Provide mappings to lookup worlds based on their name and based on
    ## their (host, port) connection pair.
    
    s.name_mapping     = dict( 
                               ( s.normalize( conf._name ), conf )
                               for conf in s.worldconfig.domains.itervalues()
                            )

    s.hostport_mapping = dict( 
                               ( ( conf._host, conf._port ), conf )
                               for conf in s.worldconfig.domains.itervalues() 
                             )
   
 
  def normalize( s, name ):

    return remove_accents( name.strip() ).lower()


  def knownWorldList( s ):

    return [ name
               for dummy, name
               in sorted (
                           ( s.normalize( conf._name ), conf._name )
                             for conf
                             in s.worldconfig.domains.itervalues()
                         )
           ]


  def newWorldConf( s, host="", port=8000, ssl=False, name="" ):

    worldconf       = s.worldconfig.createAnonymousDomain()
    worldconf._host = host
    worldconf._port = port
    worldconf._name = name
    worldconf._ssl  = ssl

    return worldconf
    

  def newWorld( s, conf ):

    return World( conf )
    

  def newAnonymousWorld( s, host="", port=8000, ssl=False ):

    conf = s.newWorldConf( host, port, ssl )
    return s.newWorld( conf )


  def lookupWorldByName( s, name ):

    conf = s.name_mapping.get( s.normalize( name ) )

    if conf:
      return s.newWorld( conf )

    return None


  def lookupWorldByHostPort( s, host, port ):

    conf = s.hostport_mapping.get( ( host, port ) )

    if conf:
      return s.newWorld( conf )

    return None

