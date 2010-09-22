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
from Matches        import SmartMatch
from Matches        import RegexMatch
from Matches        import MatchCreationError
from Matches        import load_match_by_type

import ChunkData



def trigger_type_getter( key ):

  ## This function is used by the module where the global configuration object
  ## is instantiated.

  if key == "match":
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

    chunk_type, payload = chunk

    if chunk_type != ChunkData.TEXT:
      continue

    if pos == target_pos:

      chunkbuffer.insert( i, new_chunk )
      new_chunk = None
      continue

    elif target_pos - pos < len( payload ):

      split_pos = target_pos - pos

      chunkbuffer.pop( i )
      chunkbuffer.insert( i,   ( ChunkData.TEXT, payload[ :split_pos ] ) )
      chunkbuffer.insert( i+1, new_chunk )
      chunkbuffer.insert( i+2, ( ChunkData.TEXT, payload[ split_pos: ] ) )

      pos += split_pos
      new_chunk = None
      continue

    else:
      pos += len( payload )

    if target_pos == pos:
      chunkbuffer.append( new_chunk )


class HighlightAction:

  def __init__( s, format, token=None ):

    s.name = '_'.join( ( "highlight", token ) ) if token else "highlight"

    s.highlight = ConfigTypes.FORMAT.from_string( format )
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
      ( start, ( ChunkData.HIGHLIGHT, ( id( hl ), hl ) ) ),
      ( end,   ( ChunkData.HIGHLIGHT, ( id( hl ), {} ) ) ),
    ]

    insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks )


  def __repr__( s ):

    return ConfigTypes.FORMAT.to_string( s.highlight )


  def __unicode__( s ):

    return u"highlight" + ( u" (%s)" % s.token if s.token else u"" ) + u": " \
           + ConfigTypes.FORMAT.to_string( s.highlight )



class PlayAction:

  name = "play"

  def __init__( s, soundfile=None ):

    s.soundfile = soundfile or ":/sound/pop"


  def __call__( s, match, chunkbuffer ):

    singletons.sound.play( s.soundfile )


  def __repr__( s ):

    return s.soundfile


  def __unicode__( s ):

    return s.name + u": " + s.soundfile



class GagAction:

  name = "gag"

  def __call__( s, match, chunkbuffer ):

    for i in reversed( range( len( chunkbuffer ) ) ):

      chunk = chunkbuffer[ i ]

      chunk_type, _ = chunk

      if chunk_type in ( ChunkData.TEXT,
                         ChunkData.FLOWCONTROL,
                         ChunkData.HIGHLIGHT ):
        del chunkbuffer[ i ]


  def __repr__( s ):

    return u""


  def __unicode__( s ):

    return u"gag"




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

      matches = conf.get( 'match', [] )

      match_count = 0

      for match in matches:

        type = match.lower().split( ':', 1 )[0]

        try:

          ## TODO: Should this method have to know about match types?
          if type in ( u"smart", u"regex" ):
            pattern = match[ len( type )+1: ]
            m = s.createMatch( pattern, type )

          else:
            m = s.createMatch( match )

        except MatchCreationError:
          continue

        s.addMatch( m, groupname )
        match_count += 1

      if match_count == 0:  ## No match created, presumably due to errors.
        continue

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
      group_dict[ 'match' ] = [ repr( m ) for m in s.matches[ group ] ]

      for action in s.actions.get( group, () ):
        group_dict[ action.name ] = repr( action )

      conf_dict[ ConfigBasket.SECTION_CHAR + group ] = group_dict

    new_match_conf = ConfigBasket.buildFromDict( conf_dict )

    try:
      conf.deleteSection( conf._matches_section )
    except KeyError:
      pass

    if conf_dict:
      conf.saveSection( new_match_conf, conf._matches_section )


  def createMatch( s, pattern, type=u"smart" ):

    return load_match_by_type( pattern, type )


  def addMatch( s, match, group=None ):

    if group is None:

      ## If no group name is given: use the smallest available number as the
      ## group name.

      existing_number_groups = [ int( g ) for g in s.matches.keys()
                                 if g.isdigit() ]
      new_group_number = min( i for i in range( 1, len( s.matches ) + 2 )
                              if i not in existing_number_groups )
      group = unicode( new_group_number )

    else:
      group = group.strip()

    s.matches.setdefault( group, [] ).append( match )


  def loadAction( s, actionname, args, kwargs ):

    ## TODO: Make this less hardcody. We can do it. We have the technology.

    from commands.CommandExecutor import match_args_to_function

    if actionname == "gag":
      action = GagAction

    elif actionname == "highlight":
      action = HighlightAction

    elif actionname == "play":
      action = PlayAction

    else:
      return None, u"No such action as %s!" % actionname

    ok, msg = match_args_to_function( action, args, kwargs )

    if not ok:
      return None, msg

    return action( *args, **kwargs ), None


  def addAction( s, action, group ):

    s.actions.setdefault( group, [] ).append( action )


  def hasGroup( s, group ):

    return group in s.matches or group in s.actions


  def sizeOfGroup( s, group ):

    return len( s.matches.get( group, [] ) )


  def delGroup( s, group ):

    for d in ( s.matches, s.actions ):

      try:
        del d[ group ]

      except KeyError:
        pass


  def delMatch( s, group, index ):

    try:
      s.matches[ group ].pop( index )

    except ( KeyError, IndexError ):
      pass


  def findMatches( s, line ):

    for group, matches in sorted( s.matches.iteritems() ):
      for match in matches:

        result = match.match( line )

        if result:
          yield group, result


  def performMatchingActions( s, line, chunkbuffer ):

    for group, matchresult in s.findMatches( line ):
      for action in s.actions.get( group, [] ):

        action( matchresult, chunkbuffer )


  def isEmpty( s ):

    return len( s.matches ) == 0


  def confSaveCallback( s ):

    s.save( singletons.config )
