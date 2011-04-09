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
## SettingsNode.py
##
## Holds the classes that handle the configuration subsystem.
##

u"""
:doctest:

>>> from SettingsNode import *

"""


from CallbackRegistry import CallbackRegistry
from weakref          import WeakValueDictionary

import string

VALID_KEY_CHARACTER = set( string.ascii_letters + string.digits + "_" )



class DictAttrProxy( object ):
  u"""
  This class is meant to be inherited from by dict-like subclasses, and makes
  the dict's keys accessible as attributes. Use it as a parent class, and you
  can then access:
    d[ "somekey" ]
  as:
    d._somekey
  It requires the child class to have the __{set|get|del}item__ methods of a
  dictionary.

  """


  @staticmethod
  def validatedAttr( attr ):
    u"""
    Static method. Determines whether the parameter begins with one
    underscore '_' but not two. Returns None otherwise.
    Attributes beginning with one underscore will be looked up as items on
    self.

    """

    if len( attr ) >= 2 \
      and attr.startswith( "_" ) \
      and not attr.startswith( "__" ):

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




class WeakSet( WeakValueDictionary ):

  """
  Provides a set that doesn't keep references to its contents.

  >>> class Class( object ): pass
  >>> ws = WeakSet()
  >>> a = Class() ; b = Class()
  >>> ws.add( a ) ; ws.add( b )
  >>> len( ws )
  2
  >>> del b
  >>> len( ws )
  1

  """

  __iter__ = WeakValueDictionary.itervalues
  __len__ = WeakValueDictionary.__len__

  def add( self, val ):

    self[ id( val ) ] = val



class SettingsNode( DictAttrProxy ):
  """
  Holds the core behavior for a set of configuration keys.
  """

  SEP = '.'

  def __init__( self, parent=None ):

    self.label     = None
    self.keys      = {}
    self.sections  = {}
    self.children  = WeakSet()
    self.notifiers = CallbackRegistry()

    self.setParent( parent )


  def isValidKeyName( self, key ):

    return all( c in VALID_KEY_CHARACTER for c in key )


  def __getitem__( self, key ):

    ## Attempt to resolve key as local value:

    if key in self.keys:
      return self.keys[ key ]

    ## Attempt to resolve key as section:

    if key in self.sections:
      return self.sections[ key ]

    ## If the key exists as a section on a parent, use that to create a new
    ## subsection on this object:

    if self.parent:

      try:
        self.parent.section( key )  ## If this doesn't fail with KeyError...
        return self.section( key, create_if_missing=True )

      except KeyError:

        ## Last ditch effort: get key value on parent.
        return self.parent[ key ]

    ## No parent. Abort.
    raise KeyError( key )


  def __setitem__( self, key, value ):

    if not self.isValidKeyName( key ):
      raise KeyError( "Invalid key name '%s'" % key )

    old_value = object()

    try:
      old_value = self.parent[ key ] if self.parent else old_value
    except KeyError:
      pass

    if value == old_value:  ## Always fails if old_value is a new object().

      ## If the parent's value is already set to the new value, we delete
      ## the attribute on this object instead so we'll inherit that of its
      ## parent instead.

      try:
        ## Note: this calls __delitem__, which takes care of notifications.
        del self[ key ]

      except KeyError:
        pass

      return

    marker = object()

    old_value = self.get( key, marker )

    if old_value == value:  ## Always False if old_value == marker.
      ## If the value hasn't changed, we quit right away.
      return

    self.keys[ key ] = value

    self.notifyKeyChanged( key, value )


  def __delitem__( self, key ):

    if key not in self.keys:
      raise KeyError( key )

    old_value = self.keys[ key ]

    del self.keys[ key ]

    value = object()

    if self.parent:
      try:
        value = self.parent[ key ]
      except KeyError:
        pass

    if old_value != value:  ## Always true if value is object() from above.
      self.notifyKeyChanged( key, value )


  def __contains__( self, key ):

    return key in self.keys


  def get( self, key, default=None ):
    """
    Returns the value for the given key from this object if it exists, or the
    given default otherwise.

    >>> c = SettingsNode()
    >>> c[ 'a' ] = 1
    >>> c.get( 'a', 2 )
    1
    >>> c.get( 'b', 2 )
    2

    """

    return self.keys.get( key, default )


  def section( self, name, create_if_missing=False ):
    """
    Returns the subsection with the given name.

    If it doesn't exist on this node but does on a parent, create a new section
    on this node with the corresponding name and parent, otherwise raise
    KeyError.

    If the create_if_missing parameter is True, create the section on this
    node even if if doesn't exist on a parent.

    """

    if name in self.sections:
      return self.sections[ name ]

    try:
      parent_section = self.parent.section( name ) if self.parent else None

    except KeyError:
      parent_section = None

    if not create_if_missing and parent_section is None:
      raise KeyError( u"No such section", name )

    ## Create new subsection with same class as self:
    subsection = self.sections[ name ] = self.__class__()

    if self.label:
      subsection.label = self.label

    subsection.setParent( parent_section )

    return subsection


  def setParent( self, parent ):

    self.parent = parent

    if parent:
      parent.children.add( self )


  def clear( self ):

    ## We do this by hand, so notifications are emitted appropriately.

    for key in list( self.keys.keys() ):  ## Wrapped in a list because we'll
      del self[ key ]                     ## be deleting items on the fly.


  def apply( self ):

    for k, v in self.keys.iteritems():
      self.parent[ k ] = v

    for child in self.children:
      child.apply()

    self.clear()


  def isEmpty( self ):

    return len( self.keys ) == 0 and len( self.children ) == 0


  def notifyKeyChanged( self, key, value ):

    self.notifiers.triggerAll( key, value )

    ## TODO: Only propagate to children if the new value of the parent is
    ## also new to them.

    for child in self.children:
      child.notifyKeyChanged( key, value )


  def registerNotifier( self, notifier ):

    self.notifiers.add( notifier )


  def getNodeKeyByPath( self, node_path, create_if_missing=False ):

    if self.SEP in node_path:
      node_path, key = node_path.rsplit( self.SEP, 1 )

    else:
      node_path, key = "", node_path

    node = self.getNodeByPath( node_path, create_if_missing )

    if key in node.sections:
      return node.section( key ), None

    return node, key


  def getNodeByPath( self, node_path, create_if_missing=False ):

    node = self

    for section in node_path.split( self.SEP ):

      if not section:
        continue

      node = node.section( section, create_if_missing )

    return node


  def getParentByLabel( self, label ):

    if label is self.label:
      return self

    if self.parent:
      return self.parent.getParentByLabel( label )

    return None


  def __repr__( self ):

    hid = hex( id( self ) )

    if self.label:
      return "<%s '%s' (%s)>" % ( self.__class__.__name__, self.label, hid )

    return "<%s (%s)>" % ( self.__class__.__name__, hid )
