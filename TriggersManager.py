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

import ConfigTypes

from SmartMatch     import SmartMatch
from PipelineChunks import HighlightChunk
from Singletons     import singletons


class HighlightAction:

  def __init__( s, highlight ):

    s.highlight = highlight


  def __call__( s, chunkbuffer ):

    hl = s.highlight

    chunkbuffer.insert( 0, HighlightChunk( ( id( hl ), hl ) ) )
    chunkbuffer.append(    HighlightChunk( ( id( hl ), {} ) ) )



def trigger_configuration_setup( conf ):

  section = conf._matches_section

  if not conf.hasSection( section ):
    match_conf = conf.createSection( section )

  else:
    match_conf = conf.getSection( section )

  match_groups = match_conf.getSectionList()

  matches = []
  actions = {}

  for group in match_groups:

    group_conf = match_conf.getSection( group )

    for k, v in group_conf.getOwnDict().iteritems():

      if k.startswith( "match" ):

        match = SmartMatch()
        match.setPattern( v )
        match.setName( group )
        matches.append( match )

      elif k.startswith( "highlight" ):

        action = HighlightAction( v )
        actions.setdefault( group, [] ).append( action )

  return matches, actions


def trigger_type_getter( key ):

  if key.startswith( "highlight" ):
    return ConfigTypes.FORMAT

  return ConfigTypes.STR


class TriggersManager:

  def __init__( s ):

    conf = singletons.config
    s.matches, s.actions = trigger_configuration_setup( conf )


  def lookupMatches( s, line ):

    for m in s.matches:
      if m.matches( line ):
        yield m


  def matchActions( s, match ):

    return ( action for action in s.actions.get( match.name, [] ) )


  def isEmpty( s ):

    return len( s.matches ) == 0
