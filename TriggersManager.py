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

import re
import ConfigTypes

from Singletons     import singletons
from ConfigBasket   import ConfigBasket
from Matches        import SmartMatch, RegexMatch, load_from_string
from PipelineChunks import HighlightChunk, UnicodeTextChunk, chunktypes



def trigger_type_getter( key ):

  ## This function is used by the module where the global configuration object
  ## is instantiated.

  if key.startswith( "highlight" ):
    return ConfigTypes.FORMAT

  elif key == "match":
    return ConfigTypes.STRLIST

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

    if target_pos == pos:
      chunkbuffer.append( new_chunk )


class HighlightAction:

  def __init__( s, highlight, token=None ):

    s.name = '_'.join( ( "highlight", token ) ) if token else "highlight"

    s.highlight = highlight
    s.token     = token


  def __call__( s, match, chunkbuffer ):

    if not s.token:
      start, end = match.span()

    else:

      if s.token not in match.groupdict():
        return

      start, end = match.span( s.token )

    if start == end:
      return

    hl = s.highlight

    new_chunks = [
      ( start, HighlightChunk( ( id( hl ), hl ) ) ),
      ( end,   HighlightChunk( ( id( hl ), {} ) ) ),
    ]

    insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks )


  def __unicode__( s ):

    return ConfigTypes.FORMAT.to_string( s.highlight )



class PlayAction:

  name = "play"

  def __init__( s, soundfile=None ):

    s.soundfile = soundfile or ":/sound/pop"


  def __call__( s, match, chunkbuffer ):

    singletons.sound.play( s.soundfile )


  def __unicode__( s ):

    return s.soundfile



class GagAction:

  name = "gag"

  def __call__( s, match, chunkbuffer ):

    for i in reversed( range( len( chunkbuffer ) ) ):

      chunk = chunkbuffer[ i ]

      if chunk.chunktype in ( chunktypes.TEXT,
                              chunktypes.FLOWCONTROL,
                              chunktypes.HIGHLIGHT ):
        del chunkbuffer[ i ]


  def __unicode__( s ):

    return ""




def get_matches_configuration( conf ):

  section = conf._matches_section

  if not conf.hasSection( section ):
    ## No Matches section yet. Create it.
    matches = conf.createSection( section )

  else:
    matches = conf.getSection( section )

  return dict( ( group, matches.getSection( group ).getOwnDict() )
               for group in matches.getSectionList() )




class TriggersManager:

  def __init__( s ):

    s.matches = {}
    s.actions = {}

    s.load( singletons.config )
    singletons.config.registerSaveCallback( s.confSaveCallback )


  def load( s, conf ):

    all_groups = get_matches_configuration( conf )

    for groupname, conf in all_groups.iteritems():

      matches = conf.get( 'match' )

      if not matches:
        continue

      for match in matches:
        s.addMatch( match, groupname )

      if 'gag' in conf:

        s.addAction( GagAction(), groupname )
        continue  ## If there's a gag, ignore all other actions!

      if 'play' in conf:
        s.addAction( PlayAction( conf.get( 'play' ) ), groupname )

      highlight_keys = [ k for k in conf if k.startswith( "highlight" ) ]

      for k in highlight_keys:

        if '_' in k:
          token = k.split( '_', 1 )[ -1 ]

        else:
          token = None

        s.addAction( HighlightAction( conf[ k ], token ), groupname )


  def save( s, conf ):

    ## Configuration is about to be saved. Serialize our current setup into the
    ## configuration.

    conf_dict = {}

    for group in s.matches.iterkeys():

      group_dict = {}
      group_dict[ 'match' ] = [ unicode( m ) for m in s.matches[ group ] ]

      for action in s.actions.get( group, () ):
        group_dict[ action.name ] = unicode( action )

      conf_dict[ ConfigBasket.SECTION_CHAR + group ] = group_dict

    new_match_conf = ConfigBasket.buildFromDict( conf_dict )

    try:
      conf.deleteSection( conf._matches_section )
    except KeyError:
      pass

    if conf_dict:
      conf.saveSection( new_match_conf, conf._matches_section )


  def addMatch( s, matchstring, group=None ):

    m = load_from_string( matchstring )
    ## TODO: Handle errors in match creation.

    if group is None:
      group = str( len( s.matches ) )

    s.matches.setdefault( group, [] ).append( m )


  def addAction( s, action, group ):

    s.actions.setdefault( group, [] ).append( action )


  def delGroup( s, group ):

    for d in ( s.matches, s.actions ):

      try:
        del d[ group ]

      except KeyError:
        pass


  def performMatchingActions( s, line, chunkbuffer ):

    for group, matches in sorted( s.matches.iteritems() ):

      for match in matches:

        if match.matches( line ):

          for action in s.actions.get( group, [] ):
            action( match.result, chunkbuffer )


  def isEmpty( s ):

    return len( s.matches ) == 0


  def confSaveCallback( s ):

    s.save( singletons.config )
