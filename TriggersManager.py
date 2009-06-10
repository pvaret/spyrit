# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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
## TriggersManager.py
##
## This class manages matches, triggers, and their association based on a
## given world's configuration.
##


from SmartMatch import SmartMatch

from Defaults   import MATCHES_DOMAIN


class TriggersManager:

  def __init__( s, conf ):

    s.conf = conf

    s.loadConfiguration()


  def loadConfiguration( s ):

    try:
      matches = s.conf.getDomain( MATCHES_DOMAIN )

    except KeyError:
      matches = s.conf.createDomain( MATCHES_DOMAIN )

    s.matches = []

    for match in matches.getOwnDict().itervalues():

      m = SmartMatch()
      m.setPattern( match )
      s.matches.append( m )

  
  def lookupMatch( s, line ):

    for m in s.matches:
      if m.matches( line ):
        return m

    return None


  def isEmpty( s ):

    return len( s.matches ) == 0
