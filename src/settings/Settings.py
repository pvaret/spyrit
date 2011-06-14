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
## Settings.py
##
## Implements the core settings paraphernalia.
##


from CallbackRegistry import CallbackRegistry

class __NoValue( object ):
  def __repr__( self ):
    return '<NO VALUE>'

NO_VALUE = __NoValue()


from fnmatch import fnmatchcase


class MatchingDict( dict ):

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



class Leaf( object ):

  def __init__( self, container ):

    self.inherit = None
    self.container = container
    self.own_value = NO_VALUE
    self.fallback_value = None
    self.notifier = CallbackRegistry()


  def setInherit( self, inherit ):

    self.inherit = inherit

    if inherit is not None:
      inherit.notifier.add( self.propagate )
      self.fallback_value = inherit.value()


  def value( self ):

    return self.own_value if self.own_value is not NO_VALUE \
           else self.fallback_value


  def setValue( self, value ):

    prev_value = self.value()

    if value == self.fallback_value:
      value = NO_VALUE

    self.own_value = value

    new_value = self.value()
    if new_value != prev_value:
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



class Node( object ):

  def __init__( self, container ):

    self.inherit = None
    self.proto = None
    self.container = container
    self.nodes = {}


  def setInherit( self, inherit ):

    self.inherit = inherit


  def get( self, key ):

    try:
      return self.nodes[ key ]

    except KeyError:
      if self.proto is None:
        raise

    node = self.proto.build( self, key )
    self.nodes[ key ] = node

    return node


  def __getitem__( self, key ):

    node = self.get( key )
    return node.value()


  def __setitem__( self, key, value ):

    node = self.get( key )
    node.setValue( value )


  def __delitem__( self, key ):

    node = self.get( key )
    node.delValue()


  def value( self ):

    return self



class NodeProto( object ):

  def __init__( self, klass ):

    self.nodes = MatchingDict()
    self.default_value = None
    self.klass = klass
    self.inherit = None


  def get( self, key ):

    if "." in key:
      key, subkey = key.split( "." )
      return self.get( key ).get( subkey )

    return self.nodes[ key ]


  def new( self, key, klass=Leaf ):

    subkey = None

    if "." in key:
      key, subkey = key.split( ".", 1 )
      return self.new( key, klass=Node ).new( subkey, klass )

    if key not in self.nodes:
      self.nodes[ key ] = NodeProto( klass )

    return self.nodes[ key ]


  def build( self, container, key ):

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

      while inherit_container is not None and inherit_pattern.startswith( "." ):

        inherit_pattern = inherit_pattern[ 1: ]
        inherit_container = inherit_container.container
        ## TODO: inherit from subcontainers?

      if inherit_container is None:
        raise KeyError( key )

      proto = inherit_container.proto.get( key )

    else:
      raise KeyError( key )

    node = proto.klass( container )
    node.proto = proto
    node.fallback_value = proto.default_value

    ## 2/ Set up inheritance given the provided information.

    if inherit_container is not None:

      inherit_node = inherit_container.get( key )
      node.setInherit( inherit_node )

      ## Sanity test:
      assert ( type( inherit_node ) is type( node ) ), \
             u"Type mismatch in Settings hierarchy!"

    return node



def construct_proto( schema_def ):

  pending_schema_defs = [ ( [], schema_def ) ]

  proto = current_proto = NodeProto( Node )

  while pending_schema_defs:

    current_depth, current_schema_def = pending_schema_defs.pop( 0 )
    new_proto = current_proto.new( ".".join( current_depth ), klass=Node ) \
                if current_depth else None

    if new_proto:
      new_proto.inherit = current_schema_def.get( 'inherit' )

    for key, ser in current_schema_def.get( 'keys' ):
      key = ".".join( current_depth + [ key ] )
      new_proto = current_proto.new( key )
      new_proto.default_value = ser.default

    for section_key, sub_schema_def in current_schema_def.get( 'sections', () ):
      pending_schema_defs.append( ( current_depth + [ section_key ],
                                    sub_schema_def ) )

  return proto
