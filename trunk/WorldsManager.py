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

from Singletons import singletons
from Utilities  import case_insensitive_cmp


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
    
    
  def knownWorldList( s ):

    return sorted( s.worldconfig.getDomainList(), case_insensitive_cmp )

