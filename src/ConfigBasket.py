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
## ConfigBasket.py
##
## Holds the classes that handle the configuration subsystem.
##


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



class ConfigBasket( DictAttrProxy ):
  """
  Holds the core behavior for a set of configuration keys.
  """


  def __init__( self, parent=None ):

    self.basket    = {}
    self.sections  = {}
    self.children  = WeakSet()
    self.notifiers = CallbackRegistry()

    self.setParent( parent )


  def isValidKeyName( self, key ):

    return all( c in VALID_KEY_CHARACTER for c in key )


  def __getitem__( self, key ):

    ## Attempt to resolve key as local value:
    if key in self.basket:
      return self.basket[ key ]

    ## Attempt to resolve key as local section, possibly reparented to this
    ## object's parent's similarly named subsection:
    if key in self.sections:

      section = self.sections[ key ]

      if self.parent:

        try:
          parent_section = self.parent[ key ]

        except KeyError:
          parent_section = None

      section.setParent( parent_section )
      return section

    ## Attempt to resolve key as value or section on parent:
    if self.parent:
      return self.parent[ key ]

    ## Abort:
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

    self.basket[ key ] = value

    self.notifyKeyChanged( key, value )


  def __delitem__( self, key ):

    if key not in self.basket:
      raise KeyError( key )

    old_value = self.basket[ key ]

    del self.basket[ key ]

    value = object()

    if self.parent:
      try:
        value = self.parent[ key ]
      except KeyError:
        pass

    if old_value != value:  ## Always true if value is object() from above.
      self.notifyKeyChanged( key, value )


  def __contains__( self, key ):

    return key in self.basket


  def get( self, key, default=None ):
    """
    Returns the value for the given key from this object if it exists, or the
    given default otherwise.

    >>> c = ConfigBasket()
    >>> c[ 'a' ] = 1
    >>> c.get( 'a', 2 )
    1
    >>> c.get( 'b', 2 )
    2

    """

    return self.basket.get( key, default )


  def setParent( self, parent ):

    self.parent = parent

    if parent:
      parent.children.add( self )


  def clear( self ):

    ## We do this by hand, so notifications are emitted appropriately.
    for key in list( self.basket.keys() ):  ## Wrapped in a list because we'll
      del self[ key ]                       ## be deleting items on the fly.


  def apply( self ):

    for k, v in self.basket.iteritems():
      self.parent[ k ] = v

    self.clear()


  def isEmpty( self ):

    return len( self.basket ) == 0 and len( self.children ) == 0


  def notifyKeyChanged( self, key, value ):

    self.notifiers.triggerAll( key, value )

    ## TODO: Only propagate to children if the new value of the parent is
    ## also new to them.

    for child in self.children:
      child.notifyKeyChanged( key, value )


  def registerNotifier( self, notifier ):

    self.notifiers.add( notifier )


