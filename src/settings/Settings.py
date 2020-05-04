# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## Settings.py
##
## Implements the core settings paraphernalia.
##

"""
:doctest:

>>> from settings.Settings import *

"""

from fnmatch import fnmatchcase

from CallbackRegistry import CallbackRegistry


class __NoValue( object ):
  def __repr__( self ):
    return "<NO VALUE>"


NO_VALUE = __NoValue()

## A dummy key name for the root node of the settings.
ROOT = "@"


class MatchingDict( dict ):
  """
  A dictionary whose keys are glob patterns, and where key lookup is matched
  against those patterns.

  >>> m = MatchingDict()
  >>> m[ "ab?" ] = 1
  >>> m[ "de*" ] = 2
  >>> print( m[ "abc" ] )
  1
  >>> print( m[ "defg" ] )
  2
  >>> print( "abcd" in m )
  False
  >>> print( "defg" in m )
  True

  """

  def __contains__( self, key ):

    try:
      self[ key ]
      return True

    except KeyError:
      return False

  def __getitem__( self, key ):

    try:
      return dict.__getitem__( self, key )
    except KeyError:
      pass

    for k in sorted( self.keys(), key=len, reverse=True ):
      if fnmatchcase( key, k ):
        return self[ k ]

    raise KeyError( key )


class DictAttrProxy( object ):
  """
  This class is meant to be inherited from by dict-like subclasses, and makes
  the dict's keys accessible as attributes. Use it as a parent class, and you
  can then access:
    d[ "somekey" ]
  as:
    d._somekey
  It requires the child class to have the __{set|get|del}item__ methods of a
  dictionary.

  >>> class Test( DictAttrProxy, dict ):
  ...   pass
  >>> d = Test()
  >>> d[ "a" ] = 1
  >>> d._a
  1
  >>> d._b = 2
  >>> d[ "b" ]
  2
  >>> del d._a
  >>> "a" in d
  False

  """

  @staticmethod
  def validatedAttr( attr ):
    """
    Static method. Determines whether the parameter begins with one
    underscore '_' but not two. Returns None otherwise.
    Attributes beginning with one underscore will be looked up as items on
    self.

    """

    if ( len( attr ) >= 2
         and attr.startswith( "_" )
         and not attr.startswith( "__" ) ):

        return attr[ 1: ]

    return None

  def __getattr__( self, attr ):

    vattr = self.validatedAttr( attr )

    if vattr is None:
      ## This is neither an existing native attribute, nor a 'special'
      ## attribute name that should be read off the mapped dictionary,
      ## so we raise an AttributeError.
      raise AttributeError( attr )

    try:
      return self[ vattr ]

    except KeyError:
      raise AttributeError( attr )

  def __setattr__( self, attr, value ):

    vattr = self.validatedAttr( attr )

    if vattr:
      self[ vattr ] = value

    else:
      ## If this is a 'normal' attribute, treat it the normal way.
      object.__setattr__( self, attr, value )

  def __delattr__( self, attr ):

    vattr = self.validatedAttr( attr )

    if vattr is None:
      ## If this is a 'normal' attribute, treat it the normal way
      ## and then return.
      object.__delattr__( self, attr )

      return

    try:
      del self[ vattr ]

    except KeyError:
      raise AttributeError( attr )


class Leaf( object ):

  def __init__( self, key, container ):

    self.key            = key
    self.inherit        = None
    self.notifier       = CallbackRegistry()
    self.own_value      = NO_VALUE
    self.container      = container
    self.fallback_value = None

  def isLeaf( self ):

    return True

  def __repr__( self ):

    key_path = ".".join( self.getFullPath() )
    return "<Leaf %s>: %r" % ( key_path, self.own_value )

  def getFullPath( self ):

    if self.container is None:
      return []

    return self.container.getFullPath() + [ self.key ]

  def setInherit( self, inherit ):

    self.inherit = inherit

    if inherit is not None:
      inherit.notifier.add( self.propagate )
      self.fallback_value = inherit.value()

  def value( self ):

    return ( self.own_value if self.own_value is not NO_VALUE
             else self.fallback_value )

  def setValue( self, value ):

    prev_value = self.value()

    if value == self.fallback_value:
      value = NO_VALUE

    self.own_value = value

    new_value = self.value()
    if self.notifier and ( new_value != prev_value ):
      self.notifier.triggerAll( new_value )

  def delValue( self ):

    self.setValue( NO_VALUE )

  def propagate( self, new_value ):

    prev_value = self.value()
    self.fallback_value = new_value

    if self.value() != prev_value:
      self.notifier.triggerAll( new_value )

  def isEmpty( self ):

    return self.own_value is NO_VALUE


def default_dump_predicate( node ):

  return not node.proto.metadata.get( "exclude_from_dump" )


class Node( DictAttrProxy ):

  def __init__( self, key, container ):

    self.key       = key
    self.proto     = None
    self.nodes     = {}
    self.inherit   = None
    self.container = container

  def isLeaf( self ):

    return False

  def __repr__( self ):

    return "<Node %s>" % ( ".".join( self.getFullPath() ) or "." )

  def getFullPath( self ):

    if self.container is None:
      return []

    return self.container.getFullPath() + [ self.key ]

  def setInherit( self, inherit ):

    self.inherit = inherit

  def get( self, key ):

    if "." in key:
      head, tail = key.split( ".", 1 )
      return self.get( head ).get( tail )

    try:
      return self.nodes[ key ]

    except KeyError:
      if self.proto is None:
        raise

    node = self.proto.build( key, self )
    self.nodes[ key ] = node

    return node

  def __iter__( self ):

    return iter( self.nodes )

  def __getitem__( self, key ):

    node = self.get( key )
    return node.value()

  def __setitem__( self, key, value ):

    node = self.get( key )
    node.setValue( value )

  def __delitem__( self, key ):

    node = self.get( key )
    node.delValue()

  def asDict( self ):

    ret = {}
    for k, v in self.nodes.items():
      if v.isLeaf():
        ret[ k ] = v.value()
      else:
        ret[ k ] = v.asDict()

    return ret

  def value( self ):

    return self

  def isEmpty( self ):

    return all( node.isEmpty() for node in self.nodes.values() )

  def setValue( self, value ):

    if not isinstance( value, dict ):
      raise ValueError( "Expected a dictionary-type value for key %s; "
                        "got: %r" % ( self.getFullPath(), value ) )

    try:
      for k, v in value.items():
        self.get( k ).setValue( v )
    except KeyError:
      raise ValueError( "Expected a dict matching the schema for key %s; "
                        "got %r" % ( self.getFullPath(), value ) )

  def dump( self, predicate=default_dump_predicate ):

    stack = [ ( self, "" ) ]
    result = ( {}, {} )

    KEYS     = 0
    SECTIONS = 1

    while stack:

      node, key = stack.pop( 0 )

      if node.isLeaf():

        serializer = node.proto.metadata.get( "serializer" )

        if node.isEmpty() or serializer is None or not predicate( node ):
          continue

        result[ KEYS ][ key ] = serializer.serialize( node.value() )

      else:

        for node_key, node in sorted( node.nodes.items() ):

          if node.isEmpty():
            continue

          subkey = ".".join( ( key, node_key ) ) if key else node_key

          if node.proto.metadata.get( "is_section" ):

            dump = node.dump( predicate )

            if len( dump[ KEYS ] ) + len( dump[ SECTIONS ] ) > 0:
              result[ SECTIONS ][ subkey ] = dump

          else:
            stack.append( ( node, subkey ) )

    return result

  def onChange( self, key, callback ):

    leaf = self.get( key )
    leaf.notifier.add( callback )


class NodeProto( object ):

  def __init__( self, key, klass ):

    self.key           = key
    self.nodes         = MatchingDict()
    self.klass         = klass
    self.inherit       = None
    self.metadata      = {}
    self.default_value = None

  def get( self, key ):

    if "." in key:
      key, subkey = key.split( "." )
      return self.get( key ).get( subkey )

    return self.nodes[ key ]

  def new( self, key, klass ):

    if "." in key:
      key, subkey = key.split( ".", 1 )
      return ( self.new( key, klass=Node )
                   .new( subkey, klass=klass ) )

    if key not in self.nodes:

      new_node = NodeProto( key, klass )
      self.nodes[ key ] = new_node

    return self.nodes[ key ]

  def build( self, key, container ):

    node = None
    inherit_container = None

    ## 1/ Figure out what node to build, by looking it up in the prototype tree
    ## then searching this prototype for inheritance information.

    if key in self.nodes:

      proto = self.get( key )

      if container.inherit is not None:
        inherit_container = container.inherit

    elif self.inherit:

      inherit_pattern = self.inherit
      inherit_container = container

      while ( inherit_container is not None
              and inherit_pattern.startswith( "." ) ):

        inherit_pattern = inherit_pattern[ 1: ]
        inherit_container = inherit_container.container
        ## TODO: inherit from subcontainers?

      if inherit_container is None:
        raise KeyError( key )

      proto = inherit_container.proto.get( key )

    else:
      raise KeyError( key )

    node = proto.klass( key, container )
    node.proto = proto
    node.fallback_value = proto.default_value

    ## 2/ Set up inheritance given the provided information.

    if inherit_container is not None:

      inherit_node = inherit_container.get( key )
      node.setInherit( inherit_node )

      ## Sanity test:
      assert type( inherit_node ) is type( node ), (
          "Type mismatch in Settings hierarchy!" )

    return node


class Settings( Node ):

  def __init__( self ):

    super( Settings, self ).__init__( ROOT, None )

    self.proto = NodeProto( ROOT, self.__class__ )

  def loadSchema( self, schema_def ):

    pending_schema_defs = [ ( self.proto, schema_def ) ]

    while pending_schema_defs:

      current_proto, current_schema_def = pending_schema_defs.pop( 0 )

      current_proto.inherit = current_schema_def.get( "inherit" )
      section_metadata  = current_schema_def.get( "default_metadata" ) or {}

      for key, metadata in current_schema_def.get( "keys", () ):

        new_proto = current_proto.new( key, klass=Leaf )

        new_proto.metadata.update( section_metadata )
        new_proto.metadata.update( metadata )
        new_proto.metadata[ "schema_id" ] = id( schema_def )

        default    = new_proto.metadata.get( "default" )
        serializer = new_proto.metadata.get( "serializer" )

        if None not in ( serializer, default ):
          default = serializer.deserializeDefault( default )

        new_proto.default_value = default

      sections = current_schema_def.get( "sections", () )
      for section_key, sub_schema_def in sections:

        new_proto = current_proto

        for key in section_key.split( "." ):
          new_proto = new_proto.new( key, klass=Node )
          new_proto.metadata[ "is_section" ] = True

        pending_schema_defs.append( ( new_proto, sub_schema_def ) )

  def restore( self, settings_struct ):

    stack = [ ( self, settings_struct ) ]

    while stack:

      current_settings, struct = stack.pop( 0 )
      keys, sections = struct

      for key, value in keys.items():

        try:
          node = current_settings.get( key )

        except KeyError:
          continue

        serializer = node.proto.metadata.get( "serializer" )
        if serializer is None:
          continue

        value = serializer.deserialize( value )
        node.setValue( value )

      for section, struct in sections.items():

        try:
          node = current_settings.get( section )

        except KeyError:
          continue

        if not node.isLeaf():
          stack.append( ( node, struct ) )
