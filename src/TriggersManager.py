# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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

from __future__ import absolute_import
from __future__ import unicode_literals

import os.path

from PyQt5.QtWidgets import QApplication

from Matches        import RegexMatch
from Matches        import load_match_by_type
from Globals        import URL_RE
from Globals        import FORMAT_PROPERTIES
from Utilities      import normalize_text
from OrderedDict    import OrderedDict
from SpyritSettings import MATCHES

from pipeline.ChunkData import ChunkType
from pipeline.PipeUtils import insert_chunks_in_chunk_buffer

import Serializers


class HighlightAction:

  multiple_matches_per_line = True

  @classmethod
  def factory( cls, format, token=None ):

    format = Serializers.Format().deserialize( format )

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
      ( start, ( ChunkType.HIGHLIGHT, ( id( hl ), hl ) ) ),
      ( end,   ( ChunkType.HIGHLIGHT, ( id( hl ), {} ) ) ),
    ]

    insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks )


  def __repr__( self ):

    return Serializers.Format().serialize( self.highlight )


  def toString( self ):

    return u"highlight" + ( u" (%s)" % self.token if self.token else u"" ) \
           + u": " + Serializers.Format().serialize( self.highlight )


  def __unicode__( self ):

    raise NotImplementedError( "This method doesn't exist anymore!" )



class PlayAction:

  name = "play"

  ## Don't try to play several sounds at once even if several matches are found.
  multiple_matches_per_line = False

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


  def toString( self ):

    return self.name + u": " + ( self.soundfile or "pop" )


  def __unicode__( self ):

    raise NotImplementedError( "This method doesn't exist anymore!" )



class GagAction:

  name = "gag"

  ## If a line is gagged, all processing stops right away.
  multiple_matches_per_line = False

  @classmethod
  def factory( cls ):

    return cls(), None


  def __call__( self, match, chunkbuffer ):

    for i in reversed( range( len( chunkbuffer ) ) ):

      chunk = chunkbuffer[ i ]

      chunk_type, _ = chunk

      if chunk_type in ( ChunkType.TEXT,
                         ChunkType.FLOWCONTROL,
                         ChunkType.HIGHLIGHT ):
        del chunkbuffer[ i ]


  def __repr__( self ):

    return u""


  def toString( self ):

    return u"gag"


  def __unicode__( self ):

    raise NotImplementedError( "This method doesn't exist anymore!" )




class LinkAction:

  name = "link"
  multiple_matches_per_line = True

  @classmethod
  def factory( cls, url=None ):

    return cls( url ), None


  def __init__( self, url=None ):

    self.url= url


  def __call__( self, match, chunkbuffer ):

    start, end = match.span()

    if start == end:
      return

    url = self.url

    if url is None:
      url = match.group( 0 )

    ## TODO: Allow URL substitutions?

    href = {
        FORMAT_PROPERTIES.HREF:      url,
        FORMAT_PROPERTIES.COLOR:     "#1947C4",
        FORMAT_PROPERTIES.UNDERLINE: True,
    }

    new_chunks = [
      ( start, ( ChunkType.HIGHLIGHT, ( id( href ), href ) ) ),
      ( end,   ( ChunkType.HIGHLIGHT, ( id( href ), {} ) ) ),
    ]

    insert_chunks_in_chunk_buffer( chunkbuffer, new_chunks )


  def __repr__( self ):

    return u"" if self.url is None else self.url


  def toString( self ):

    return u"link"


  def __unicode__( self ):

    raise NotImplementedError( "This method doesn't exist anymore!" )




class MatchGroup:

  def __init__( self, name ):

    self.name    = name.strip()
    self.matches = []
    self.actions = OrderedDict()


  def addMatch( self, match ):

    self.matches.append( match )
    return self


  def addAction( self, action ):

    self.actions[ action.name ] = action
    return self


  def __len__( self ):

    return len( self.matches )



DEFAULT_MATCHES = [
    MatchGroup( "*HTTP_LINKS*" )
        .addMatch( RegexMatch( URL_RE ) )
        .addAction( LinkAction() ),
]


class TriggersManager:

  def __init__( self, settings ):

    self.actionregistry = {}
    self.groups = OrderedDict()
    self.load( settings )

  def registerAction( self, actionname, action ):

    assert actionname not in self.actionregistry
    self.actionregistry[ actionname ] = action

  def load( self, settings ):

    all_groups = settings[ MATCHES ]

    for groupname, node in all_groups.nodes.items():

      matches = node.get( 'match' ).value() or []

      matchgroup = None

      for match in matches:

        if not match:
          continue

        if not matchgroup:
          matchgroup = self.createOrGetMatchGroup( groupname )

        matchgroup.addMatch( match )

      if not matchgroup:  ## No match created, presumably due to errors.
        continue

      if 'gag' in node.nodes:

        action, _ = GagAction.factory()
        if action:
          matchgroup.addAction( action )

        continue  ## If there's a gag, ignore all other actions!

      if 'play' in node.nodes:

        action, _ = PlayAction.factory( node.get( 'play' ).value() )
        if action:
          matchgroup.addAction( action )

      highlight_keys = [ k for k in node.nodes if k.startswith( "highlight" ) ]

      for k in highlight_keys:

        if '_' in k:
          token = k.split( '_', 1 )[ -1 ]

        else:
          token = None

        action, _ = HighlightAction.factory( node[ k ], token )
        if action:
          matchgroup.addAction( action )


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
      group = u"%d" % new_group_number

    key = normalize_text( group.strip() )

    return self.groups.setdefault( key, MatchGroup( group ) )


  def loadAction( self, actionname, args, kwargs ):

    from commands.CommandExecutor import match_args_to_function

    action = self.actionregistry.get( actionname )
    if action is None:
      return None, u"%s: No such action!" % actionname

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

    for matchgroup in DEFAULT_MATCHES + list( self.groups.values() ):
      for match in matchgroup.matches:
        for result in match.matches( line ):
          yield matchgroup, result


  def performMatchingActions( self, line, chunkbuffer ):

    already_performed_on_this_line = set()

    for matchgroup, matchresult in self.findMatches( line ):
      for action in matchgroup.actions.values():

        ## TODO: make this cleaner. Using the class is not nice. Ideally we'd
        ## overhaul the action serialization system and reserve the 'name'
        ## attribute for this.
        action_class = id( action.__class__ )
        if action_class in already_performed_on_this_line \
            and not action.multiple_matches_per_line:
          continue
        already_performed_on_this_line.add( action_class )

        action( matchresult, chunkbuffer )


  def isEmpty( self ):

    return not self.groups


  def save( self, settings ):

    ## Configuration is about to be saved. Serialize our current setup into the
    ## configuration.

    try:
      del settings.nodes[ MATCHES ]

    except KeyError:
      pass

    for groupname, matchgroup in self.groups.items():

      node = settings[ MATCHES ].get( groupname )
      node[ 'match' ] = matchgroup.matches

      for action in matchgroup.actions.values():
        node[ action.name ] = repr( action )


def construct_triggersmanager( settings ):
  t = TriggersManager( settings )
  t.registerAction( "gag",       GagAction )
  t.registerAction( "highlight", HighlightAction )
  t.registerAction( "link",      LinkAction )
  t.registerAction( "play",      PlayAction )
  return t
