# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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


from SmartMatch     import SmartMatch
from PipelineChunks import HighlightChunk

from Defaults import MATCHES_SECTION, HIGHLIGHTS_SECTION


class HighlightAction:

  def __init__( s, highlight ):

    s.highlight = highlight


  def __call__( s, chunkbuffer ):

    hl = s.highlight

    chunkbuffer.insert( 0, HighlightChunk( ( id( hl ), hl ) ) )
    chunkbuffer.append(    HighlightChunk( ( id( hl ), {} ) ) )




class TriggersManager:

  def __init__( s, conf ):

    s.conf    = conf
    s.matches = []
    s.actions = {}

    s.loadConfiguration()


  def loadConfiguration( s ):

    ## TODO: Ugly. The TriggersManager shouldn't have to deal with
    ## configuration setup details.

    try:
      matches = s.conf.getSection( MATCHES_SECTION )

    except KeyError:
      matches = s.conf.createSection( MATCHES_SECTION )

    try:
      highlights = s.conf.getSection( HIGHLIGHTS_SECTION )

    except KeyError:
      highlights = s.conf.createSection( HIGHLIGHTS_SECTION )


    s.matches = []

    for name, match in matches.getOwnDict().iteritems():

      m = SmartMatch()
      m.setName( name )
      m.setPattern( match )

      if name in highlights.getOwnDict():
        s.actions.setdefault( name, [] ).append( HighlightAction( highlights[ name ] ) )

      s.matches.append( m )

  
  def lookupMatches( s, line ):

    for m in s.matches:
      if m.matches( line ):
        yield m


  def matchActions( s, match ):

    return ( action for action in s.actions.get( match.name, [] ) )


  def isEmpty( s ):

    return len( s.matches ) == 0
