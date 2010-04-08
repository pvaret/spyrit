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
from PipelineChunks import HighlightChunk, UnicodeTextChunk, chunktypes
from Singletons     import singletons



def trigger_type_getter( key ):

  ## This function is used by the module where the global configuration object
  ## is instantiated.

  if key.startswith( "highlight" ):
    return ConfigTypes.FORMAT

  return ConfigTypes.STR



def insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks ):

  pos       = 0
  new_chunk = None

  for i, chunk in enumerate( chunkbuffer ):

    if not new_chunk:  ## Pop the next chunk to insert...

      if not new_chunks:  ## ... Assuming there is one, of course.
        return

      target_pos, new_chunk = new_chunks.pop( 0 )

    if chunk.chunktype != chunktypes.TEXT:
      continue

    if pos == target_pos:

      chunkbuffer.insert( i, new_chunk )
      new_chunk = None
      continue

    elif target_pos - pos < len( chunk.data ):

      split_pos = target_pos - pos

      chunkbuffer.pop( i )
      chunkbuffer.insert( i,   UnicodeTextChunk( chunk.data[ :split_pos ] ) )
      chunkbuffer.insert( i+1, new_chunk )
      chunkbuffer.insert( i+2, UnicodeTextChunk( chunk.data[ split_pos: ] ) )

      pos += split_pos
      new_chunk = None
      continue

    else:
      pos += len( chunk.data )

  if pos == end:
    chunkbuffer.append( new_chunk )



class HighlightAction:

  def __init__( s, highlight, token ):

    s.highlight = highlight
    s.token     = token


  def __call__( s, match, chunkbuffer ):

    hl = s.highlight

    if not s.token:

      chunkbuffer.insert( 0, HighlightChunk( ( id( hl ), hl ) ) )
      chunkbuffer.append(    HighlightChunk( ( id( hl ), {} ) ) )

    else:

      if not s.token in match.positions:
        return

      start, end = match.positions[ s.token ]

      if start == end:
        return

      new_chunks = [
        ( start, HighlightChunk( ( id( hl ), hl ) ) ),
        ( end,   HighlightChunk( ( id( hl ), {} ) ) ),
      ]

      insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks )





def get_matches_configuration( conf ):

  section = conf._matches_section

  if not conf.hasSection( section ):
    matches = conf.createSection( section )

  else:
    matches = conf.getSection( section )

  return dict( ( group, matches.getSection( group ) )
               for group in matches.getSectionList() )



def load_matches( groups ):

  matches = []

  for group, group_conf in groups.iteritems():

    actiongroup = []

    for k, v in group_conf.getOwnDict().iteritems():

      if k.startswith( "match" ):

        match = SmartMatch()

        match.setPattern( v )
        match.setName( group )
        match.setActionGroup( actiongroup )

        matches.append( match )

      elif k.startswith( "highlight" ):

        token = None

        if "_" in k:
          token = k.split( "_", 1 )[-1]

        action = HighlightAction( v, token )
        actiongroup.append( action )

  return matches




class TriggersManager:

  def __init__( s ):

    conf = singletons.config

    all_groups = get_matches_configuration( conf )
    s.matches = load_matches( all_groups )


  def lookupMatches( s, line ):

    for m in s.matches:
      if m.matches( line ):
        yield m


  def isEmpty( s ):

    return len( s.matches ) == 0
