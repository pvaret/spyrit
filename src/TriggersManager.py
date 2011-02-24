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
## TriggersManager.py
##
## This class manages matches, triggers, and their association based on a
## given world's configuration.
##

import os.path

from PyQt4.QtGui  import QApplication

import ConfigTypes

from ConfigBasket import ConfigBasket
from Matches      import MatchCreationError
from Matches      import load_match_by_type
from OrderedDict  import OrderedDict
from Utilities    import normalize_text

from pipeline     import ChunkData



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

  @classmethod
  def factory( cls, format, token=None ):

    format = ConfigTypes.FORMAT.from_string( format )

    if not format:
      return None, u"Invalid format!"

    return cls( format, token ), None


  def __init__( self, format, token=None ):

    self.name = '_'.join( ( "highlight", token ) ) if token else "highlight"

    self.highlight = format
    self.token     = token


  def __call__( self, match, chunkbuffer ):

    if not self.token:
      start, end = match.span()

    else:

      if self.token not in match.groupdict():
        return

      start, end = match.span( self.token )

    if start == end:
      return

    hl = self.highlight

    new_chunks = [
      ( start, ( ChunkData.HIGHLIGHT, ( id( hl ), hl ) ) ),
      ( end,   ( ChunkData.HIGHLIGHT, ( id( hl ), {} ) ) ),
    ]

    insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks )


  def __repr__( self ):

    return ConfigTypes.FORMAT.to_string( self.highlight )


  def __unicode__( self ):

    return u"highlight" + ( u" (%s)" % self.token if self.token else u"" ) \
           + u": " + ConfigTypes.FORMAT.to_string( self.highlight )



class PlayAction:

  name = "play"

  @classmethod
  def factory( cls, soundfile=None ):

    if soundfile:

      soundfile = os.path.expanduser( soundfile )

      if not os.path.isfile( soundfile ):
        return None, u"File not found!"

    return cls( soundfile ), None


  def __init__( self, soundfile=None ):

    self.soundfile = soundfile


  def __call__( self, match, chunkbuffer ):

    QApplication.instance().core.sound.play( self.soundfile or ":/sound/pop" )


  def __repr__( self ):

    return self.soundfile or ""


  def __unicode__( self ):

    return self.name + u": " + ( self.soundfile or "pop" )



class GagAction:

  name = "gag"

  @classmethod
  def factory( cls ):

    return cls(), None


  def __call__( self, match, chunkbuffer ):

    for i in reversed( range( len( chunkbuffer ) ) ):

      chunk = chunkbuffer[ i ]

      chunk_type, _ = chunk

      if chunk_type in ( ChunkData.TEXT,
                         ChunkData.FLOWCONTROL,
                         ChunkData.HIGHLIGHT ):
        del chunkbuffer[ i ]


  def __repr__( self ):

    return u""


  def __unicode__( self ):

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





class MatchGroup:

  def __init__( self, name ):

    self.name    = name.strip()
    self.matches = []
    self.actions = OrderedDict()


  def addMatch( self, match ):

    self.matches.append( match )


  def addAction( self, action ):

    self.actions[ action.name ] = action


  def __len__( self ):

    return len( self.matches )



class TriggersManager:

  def __init__( self, config ):

    self.groups = {}

    self.load( config )
    config.registerSaveCallback( self.confSaveCallback )


  def load( self, conf ):

    all_groups = get_matches_configuration( conf )

    for groupname, conf in all_groups.iteritems():

      matches = conf.get( 'match', [] )

      matchgroup = None

      for match in matches:

        type = match.lower().split( ':', 1 )[0]

        try:

          ## TODO: Should this method have to know about match types?
          if type in ( u"smart", u"regex" ):
            pattern = match[ len( type )+1: ]
            m = self.createMatch( pattern, type )

          else:
            m = self.createMatch( match )

        except MatchCreationError:
          continue

        if not matchgroup:
          matchgroup = self.createOrGetMatchGroup( groupname )

        matchgroup.addMatch( m )

      if not matchgroup:  ## No match created, presumably due to errors.
        continue

      if 'gag' in conf:

        action, _ = GagAction.factory()
        if action:
          matchgroup.addAction( action )

        continue  ## If there's a gag, ignore all other actions!

      if 'play' in conf:

        action, _ = PlayAction.factory( conf.get( 'play' ) )
        if action:
          matchgroup.addAction( action )

      highlight_keys = [ k for k in conf if k.startswith( "highlight" ) ]

      for k in highlight_keys:

        if '_' in k:
          token = k.split( '_', 1 )[ -1 ]

        else:
          token = None

        action, _ = HighlightAction.factory( conf[ k ], token )
        if action:
          matchgroup.addAction( action )


  def save( self, conf ):

    ## Configuration is about to be saved. Serialize our current setup into the
    ## configuration.

    conf_dict = {}

    for matchgroup in self.groups.itervalues():

      group_dict = {}
      group_dict[ 'match' ] = [ repr( m ) for m in matchgroup.matches ]

      for action in matchgroup.actions.itervalues():
        group_dict[ action.name ] = repr( action )

      conf_dict[ ConfigBasket.SECTION_CHAR + matchgroup.name ] = group_dict

    new_match_conf = ConfigBasket.buildFromDict( conf_dict )

    try:
      conf.deleteSection( conf._matches_section )
    except KeyError:
      pass

    if conf_dict:
      conf.saveSection( new_match_conf, conf._matches_section )


  def createMatch( self, pattern, type=u"smart" ):

    return load_match_by_type( pattern, type )


  def createOrGetMatchGroup( self, group=None ):

    if group is None:

      ## If no group name is given: use the smallest available number as the
      ## group name.

      existing_number_groups = [ int( g ) for g in self.groups.keys()
                                 if g.isdigit() ]
      new_group_number = min( i for i in range( 1, len( self.groups ) + 2 )
                              if i not in existing_number_groups )
      group = unicode( new_group_number )

    key = normalize_text( group.strip() )

    return self.groups.setdefault( key, MatchGroup( group ) )


  def loadAction( self, actionname, args, kwargs ):

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

    factory = action.factory
    ok, msg = match_args_to_function( factory, args, kwargs )

    if not ok:
      return None, msg

    return factory( *args, **kwargs )


  def hasGroup( self, group ):

    return normalize_text( group.strip() ) in self.groups


  def sizeOfGroup( self, group ):

    key = normalize_text( group.strip() )

    return len( self.groups.get( key, [] ) )


  def delGroup( self, group ):

    try:
      del self.groups[ normalize_text( group.strip() ) ]

    except KeyError:
      pass


  def delMatch( self, group, index ):

    try:
      self.groups[ normalize_text( group.strip() ) ].matches.pop( index )

    except ( KeyError, IndexError ):
      pass


  def delAction( self, group, index ):

    try:
      actions = self.groups[ normalize_text( group.strip() ) ].actions

      key = list( k for k in actions )[ index ]
      del actions[ key ]

    except ( KeyError, IndexError ):
      pass


  def findMatches( self, line ):

    for matchgroup in sorted( self.groups.itervalues() ):
      for match in matchgroup.matches:

        result = match.match( line )

        if result:
          yield matchgroup, result


  def performMatchingActions( self, line, chunkbuffer ):

    for matchgroup, matchresult in self.findMatches( line ):
      for action in matchgroup.actions.itervalues():

        action( matchresult, chunkbuffer )


  def isEmpty( self ):

    return len( self.groups ) == 0


  def confSaveCallback( self ):

    config = QApplication.instance().core.config
    self.save( config )
