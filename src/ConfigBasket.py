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

VALID_KEY_CHARACTER = string.ascii_letters + string.digits + "_"


## ---[ Class DictAttrProxy ]------------------------------------------

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



## ---[ Class WeakSet ]--------------------------------------------

class WeakSet( WeakValueDictionary ):

  __iter__ = WeakValueDictionary.itervalues

  def add( self, val ):

    self[ id( val ) ] = val


## ---[ Class ConfigBasket ]---------------------------------------

class ConfigBasket( DictAttrProxy ):
  """
  Holds the core behavior for a set of configuration keys.
  """

  SECTION_CHAR = "@"


  def __init__( self, parent=None ):

    self.name      = None
    self.basket    = {}
    self.sections  = {}
    self.children  = WeakSet()
    self.notifiers = CallbackRegistry()

    self.setParent( parent )


  def isValidKeyName( self, key ):

    return all( c in VALID_KEY_CHARACTER for c in key )


  def __getitem__( self, key ):

    if key in self.basket:
        return self.basket[ key ]

    if self.parent:
        return self.parent[ key ]

    raise KeyError( key )


  def __setitem__( self, key, value ):

    if not self.isValidKeyName( key ):
      raise KeyError( "Invalid key name '%s'" % key )

    if self.parent and key in self.parent and self.parent[ key ] == value:

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

    if old_value != value:
      self.notifyKeyChanged( key, value )


  def __delitem__( self, key ):

    if key not in self.basket:
      raise KeyError( key )

    old_value = self[ key ]

    del self.basket[ key ]

    if self.parent and key in self.parent:
      value = self.parent[ key ]

      if old_value != value:
        self.notifyKeyChanged( key, value )


  def setParent( self, parent ):

    self.parent = parent

    if parent:
      parent.children.add( self )


  def clear( self ):

    ## We do this by hand, so notifications are emitted appropriately.
    for key in self.basket:
      del self[ key ]


  def isEmpty( self ):

    return len( self.basket ) == 0 and len( self.sections ) == 0


  def hasSection( self, section ):

    return self.sections.has_key( section )


  def getSection( self, section ):

    try:
      return self.sections[ section ]

    except KeyError:
      raise KeyError( "This configuration object doesn't have a section "
                    + "called %s." % section )


  def getSectionList( self ):

    return list( self.sections.iterkeys() )


  def saveSection( self, section, name ):

    section.name = name
    section.setParent( self )

    self.sections[ name ] = section


  def saveAsSection( self, name ):

    ## Watch the difference with the above method: here, THIS object is being
    ## saved into its PARENT as a new section.

    self.parent.saveSection( self, name )


  def renameSection( self, oldname, newname ):

    ## Warning: this function doesn't check whether the new section name is
    ## already in use -- if so, that section will be overridden. In other
    ## words, this is an 'mv' and not 'mv -i'.
    ## Code that makes use of this method should check that 'newname' is free,
    ## if it thinks it matters.

    section = self.getSection( oldname )  ## Raises KeyError if no such section.
    self.deleteSection( oldname )
    section.saveAsSection( newname )


  def deleteSection( self, name ):

    try:
      del self.sections[ name ]

    except KeyError:
      raise KeyError( "This configuration object doesn't have a section "
                    + "called %s." % name )


  def createAnonymousSection( self ):

    return ConfigBasket( self )


  def createSection( self, name ):

    c = self.createAnonymousSection()
    c.saveAsSection( name )

    return c


  def isAnonymous( self ):

    return self.name is None


  def notifyKeyChanged( self, key, value ):

    self.notifiers.triggerAll( key, value )

    ## TODO: Only propagate to childrens if the new value of the parent is
    ## also new to them.

    for child in self.children:
      child.notifyKeyChanged( key, value )


  def registerNotifier( self, notifier ):

    self.notifiers.add( notifier )


  def apply( self ):

    self.parent.updateFromDict( self.basket )
    self.clear()
