# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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


## ---[ Class MetaDictProxy ]------------------------------------------

class MetaDictProxy( type ):
  """
  MetaDictProxy( type )
  
  Metaclass that makes the items of a dictionary-like class accessible
  as attributes. Set it as a the metaclass for that class, and you can
  then access:
    d[ "somekey" ]
  as:
    d._somekey
  It requires the target class to have the __{set|get|del}item__ methods
  of a dictionary.
  """

  def __init__( cls, name, bases, dict ):
    
    super( MetaDictProxy, cls ).__init__( name, bases, dict )
    setattr( cls, '__setattr__', MetaDictProxy.__mysetattr )
    setattr( cls, '__getattr__', MetaDictProxy.__mygetattr )
    setattr( cls, '__delattr__', MetaDictProxy.__mydelattr )


  @staticmethod
  def validatedAttr( attr ):
    """
    Static method. Determines whether the parameter begins with one
    underscore '_' but not two. Returns None otherwise.
    Attributes beginning with one underscore will be looked up in the
    mapped dictionary.
    """
  
    if len( attr ) >= 2 \
      and attr.startswith( "_" ) \
      and not attr.startswith( "__" ):
  
        return attr[ 1: ]
  
    return None
  
  
  @staticmethod
  def __mygetattr( obj, attr ):
 
    vattr = MetaDictProxy.validatedAttr( attr )

    if vattr is None:      
      ## This is neither an existing native attribute, nor a 'special'
      ## attribute name that should be read off the mapped dictionary,
      ## so we raise an AttributeError.
      raise AttributeError( attr )
    
    try:
      return obj[ vattr ]    

    except KeyError:
      raise AttributeError( attr )
  
  
  @staticmethod
  def __mysetattr( obj, attr, value ):
  
    vattr = MetaDictProxy.validatedAttr( attr )
      
    if vattr is None:
      ## If this is a 'normal' attribute, treat it the normal way
      ## and then return.
      obj.__dict__[ attr ] = value
      return
  
    obj[ vattr ] = value
  
  
  @staticmethod
  def __mydelattr( obj, attr ):
    
    vattr = MetaDictProxy.validatedAttr( attr )
  
    if vattr is None:
      ## If this is a 'normal' attribute, treat it the normal way
      ## and then return.
      try:
        del obj.__dict__[ attr ]
        
      except KeyError:
        raise AttributeError( attr )
        
      return
      
    try:
      del obj[ vattr ]
      
    except KeyError:
      raise AttributeError( attr )



## ---[ Class WeakList ]-------------------------------------------

class WeakList( WeakValueDictionary ):

  __iter__ = WeakValueDictionary.itervalues

  def append( s, val ):

    s[ id( val ) ] = val


## ---[ Class AutoType ]-------------------------------------------

class AutoType:

  def __init__( s, type_ ):

    s.type = type_


  def get( s, *args ):

    return s.type


## ---[ Class ConfigBasket ]---------------------------------------

class ConfigBasket( object ):
  """
  ConfigBasket( object )
  
  This class holds the core behavior for a set of configuration keys.
  """

  __metaclass__ = MetaDictProxy

  SECTIONS = "__sections__"


  def __init__( s, parent=None, schema=None, autotypes=None ):

    s.name      = None
    s.basket    = {}
    s.sections  = {}
    s.types     = {}
    s.children  = WeakList()
    s.notifiers = CallbackRegistry()

    s.autotypes = autotypes and dict( autotypes ) or None

    s.setParent( parent )

    if schema: s.setSchema( schema )


  def __getitem__( s, key ):

    if key in s.basket: return s.basket[ key ]
    if s.parent:        return s.parent[ key ]

    raise KeyError( key )


  def __setitem__( s, key, value ):
    
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


  def setSchema( s, schema ):

    ## schema is to be a list of triplets (name of key, default value, type).

    d = ConfigBasket()

    types  = dict( ( k, t ) for k, v, t in schema )
    values = dict( ( k, v ) for k, v, t in schema )

    d.setTypes( types )
    d.updateFromDict( values )

    s.setParent( d )


  def setParent( s, parent ):

    s.parent = parent

    if parent:
      parent.children.append( s )


  def setTypes( s, types ):

    s.types = types


  def getType( s, key ):

    if s.types:
      return s.types.get( key )

    if s.parent:
      return s.parent.getType( key )

    else:
      return None


  def getAutoTypes( s ):

    if s.autotypes:
      return s.autotypes

    if s.parent:
      return s.parent.getAutoTypes()

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

    autotypes = s.getAutoTypes()

    if autotypes:

      type_ = autotypes.get( name )

      if type_:
        section.setTypes( AutoType( type_ ) )

    s.sections[ name ] = section


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
                    + "called %s." % section )


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

    if s.sections:
      d[ s.SECTIONS ] = dict( [ ( name, s.sections[ name ].dumpAsDict() ) \
                                  for name in s.sections ] )
    return d


  @staticmethod
  def buildFromDict( d ):

    c=ConfigBasket()
    c.updateFromDictTree( d )

    return c


  def updateFromDictTree( s, d ):

    if ConfigBasket.SECTIONS in d:

      sections = d[ ConfigBasket.SECTIONS ]

      for name, section in sections.iteritems():
        s.saveSection( ConfigBasket.buildFromDict( section ), name )

      del d[ ConfigBasket.SECTIONS ]
    
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
