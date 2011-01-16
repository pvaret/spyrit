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
  """
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
    """
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


  def __getattr__( s, attr ):

    vattr = s.validatedAttr( attr )

    if vattr is None:
      ## This is neither an existing native attribute, nor a 'special'
      ## attribute name that should be read off the mapped dictionary,
      ## so we raise an AttributeError.
      raise AttributeError( attr )

    try:
      return s[ vattr ]

    except KeyError:
      raise AttributeError( attr )


  def __setattr__( s, attr, value ):

    vattr = s.validatedAttr( attr )

    if vattr:
      s[ vattr ] = value

    else:
      ## If this is a 'normal' attribute, treat it the normal way.
      object.__setattr__( s, attr, value )


  def __delattr__( s, attr ):

    vattr = s.validatedAttr( attr )

    if vattr is None:
      ## If this is a 'normal' attribute, treat it the normal way
      ## and then return.
      object.__delattr__( s, attr )

      return

    try:
      del s[ vattr ]

    except KeyError:
      raise AttributeError( attr )



## ---[ Class WeakList ]-------------------------------------------

class WeakList( WeakValueDictionary ):

  __iter__ = WeakValueDictionary.itervalues

  def append( s, val ):

    s[ id( val ) ] = val


## ---[ Class ConfigBasket ]---------------------------------------

class ConfigBasket( DictAttrProxy ):
  """
  Holds the core behavior for a set of configuration keys.
  """

  SECTION_CHAR = "@"


  def __init__( s, parent=None ):

    s.name        = None
    s.basket      = {}
    s.sections    = {}
    s.children    = WeakList()
    s.notifiers   = CallbackRegistry()
    s.type_getter = None

    s.type_getter_for_subsection = {}

    s.setParent( parent )


  def isValidKeyName( s, key ):

    return all( c in VALID_KEY_CHARACTER for c in key )


  def __getitem__( s, key ):

    if key in s.basket: return s.basket[ key ]
    if s.parent:        return s.parent[ key ]

    raise KeyError( key )


  def __setitem__( s, key, value ):

    if not s.isValidKeyName( key ):
      raise KeyError( "Invalid key name '%s'" % key )

    if s.existsInParent( key ) and s.parent[ key ] == value:

      ## If the parent's value is already set to the new value, we delete
      ## the attribute on this object instead so we'll inherit that of its
      ## parent instead.

      try:
        ## Note: this calls __delitem__, which takes care of notifications.
        del s[ key ]

      except KeyError:
        pass

      return

    if s.exists( key ):

      old_value = s[ key ]

      if old_value == value:
        ## If the value hasn't changed, we quit right away.
        return

    else:
      old_value = None

    s.basket[ key ] = value

    if old_value != value:
      s.notifyKeyChanged( key, value )


  def __delitem__( s, key ):

    if not s.owns( key ):
      raise KeyError( key )

    old_value = s[ key ]

    del s.basket[ key ]

    if s.exists( key ):

      value = s[ key ]

      if old_value != value:
        s.notifyKeyChanged( key, value )


  def setParent( s, parent ):

    s.parent = parent

    if parent:
      parent.children.append( s )


  def setTypeGetter( s, type_getter ):

    s.type_getter = type_getter


  def setTypeGetterForFutureSections( s, type_getter_map ):

    ## Sometimes, you need to tell a ConfigBasket ahead of time that it will
    ## need a specific type getter for some future subsection or other.
    ## If so, you can set it with this method.

    s.type_getter_for_subsection = type_getter_map


  def getType( s, key ):

    if s.type_getter:

      t = s.type_getter( key )

      if t:
        return t

    if s.parent:
      return s.parent.getType( key )

    else:
      return None


  def reset( s ):

    keys = s.basket.keys()

    for key in keys:
      del s[ key ]


  def resetSections( s ):

    s.sections.clear()


  def owns( s, key ):

    return key in s.basket


  def existsInParent( s, key ):

    if s.parent:
      return s.parent.exists( key )

    return False


  def exists( s, key ):

    return s.owns( key ) or s.existsInParent( key )


  def updateFromDict( s, d ):

    for k, v in d.iteritems():

      if not k.startswith( s.SECTION_CHAR ):
        s[ k ] = v


  def isEmpty( s ):

    return len( s.basket ) == 0 and len( s.sections ) == 0


  def hasSection( s, section ):

    return s.sections.has_key( section )


  def getSection( s, section ):

    try:
      return s.sections[ section ]

    except KeyError:
      raise KeyError( "This configuration object doesn't have a section "
                    + "called %s." % section )


  def getSectionList( s ):

    return list( s.sections.iterkeys() )


  def saveSection( s, section, name ):

    section.name = name
    section.setParent( s )

    s.sections[ name ] = section

    type_getter = s.type_getter_for_subsection.get( name )

    if type_getter:
      section.setTypeGetter( type_getter )


  def saveAsSection( s, name ):

    ## Watch the difference with the above method: here, THIS object is being
    ## saved into its PARENT as a new section.

    s.parent.saveSection( s, name )


  def renameSection( s, oldname, newname ):

    ## Warning: this function doesn't check whether the new section name is
    ## already in use -- if so, that section will be overridden. In other
    ## words, this is an 'mv' and not 'mv -i'.
    ## Code that makes use of this method should check that 'newname' is free,
    ## if it thinks it matters.

    section = s.getSection( oldname )  ## Raises KeyError if no such section.
    s.deleteSection( oldname )
    section.saveAsSection( newname )


  def deleteSection( s, name ):

    try:
      del s.sections[ name ]

    except KeyError:
      raise KeyError( "This configuration object doesn't have a section "
                    + "called %s." % name )


  def createAnonymousSection( s ):

    return ConfigBasket( s )


  def createSection( s, name ):

    c = s.createAnonymousSection()
    c.saveAsSection( name )

    return c


  def isAnonymous( s ):

    return s.name is None


  def getOwnDict( s ):

    return s.basket


  def dumpAsDict( s ):

    d = s.getOwnDict().copy()

    d.update( dict( ( s.SECTION_CHAR + name, section.dumpAsDict() )
                      for name, section in s.sections.iteritems() ) )

    return d


  @staticmethod
  def buildFromDict( d ):

    c=ConfigBasket()
    c.updateFromDictTree( d )

    return c


  def updateFromDictTree( s, d ):

    for name, section in d.iteritems():

      if name.startswith( s.SECTION_CHAR ):
        s.saveSection( ConfigBasket.buildFromDict( section ), name[1:] )

    s.updateFromDict( d )


  def notifyKeyChanged( s, key, value ):

    s.notifiers.triggerAll( key, value )

    ## TODO: Only propagate to childrens if the new value of the parent is
    ## also new to them.

    for child in s.children:
      child.notifyKeyChanged( key, value )


  def registerNotifier( s, notifier ):

    s.notifiers.add( notifier )


  def commit( s ):

    s.parent.updateFromDict( s.basket )
    s.reset()
