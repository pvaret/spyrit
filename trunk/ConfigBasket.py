# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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



  class NotSpecialAttributeName( AttributeError ):
    """
    NotSpecialAttributeName( AttributeError )
  
    Internal use only.
    This exception is used to distinguish between 'normal' attributes
    and the ones, identified by having one '_' as their first character,
    that are to be magically mapped to dictionary keys by the
    MetaDictProxy metaclass.
    """
    pass




  @staticmethod
  def validatedAttr( attr ):
    """
    validatedAttr( attr )
    
    Static method. Determines whether the parameter begins with one
    underscore '_' but not two. Raises NotSpecialAttributeName otherwise.
    Attributes beginning with one underscore will be looked up in the
    mapped dictionary.
    """
  
    if len( attr ) >= 2 \
      and attr.startswith( "_" ) \
      and not attr.startswith( "__" ):
  
        return attr[ 1: ]
  
    raise MetaDictProxy.NotSpecialAttributeName( attr )
  
  
  @staticmethod
  def __mygetattr( obj, attr ):
 
    try:
      vattr = MetaDictProxy.validatedAttr( attr )
      
    except MetaDictProxy.NotSpecialAttributeName:
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
  
    try:
      attr = MetaDictProxy.validatedAttr( attr )
      
    except MetaDictProxy.NotSpecialAttributeName:
      ## If this is a 'normal' attribute, treat it the normal way
      ## and then return.
      obj.__dict__[ attr ] = value
      return
  
    obj[ attr ] = value
  
  
  @staticmethod
  def __mydelattr( obj, attr ):
    
    try:
      vattr = MetaDictProxy.validatedAttr( attr )
  
    except MetaDictProxy.NotSpecialAttributeName:
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



## ---[ Class WeakList ]---------------------------------------

class WeakList( WeakValueDictionary ):

  __iter__ = WeakValueDictionary.itervalues

  def append( s, val ):

    s[ id( val ) ] = val


## ---[ Class ConfigBasket ]---------------------------------------

class ConfigBasket( object ):
  """
  ConfigBasket( object )
  
  This class holds the core behavior for a set of configuration keys.
  """

  __metaclass__ = MetaDictProxy

  SECTIONS = "__domains__"


  def __init__( s, parent=None, schema=None ):

    s.name      = None
    s.basket    = {}
    s.domains   = {}
    s.types     = {}
    s.children  = WeakList()
    s.notifiers = CallbackRegistry()

    s.setParent( parent )

    if schema: s.setSchema( schema )


  def __getitem__( s, k ):

    k = k.lower().strip()

    try:
      return s.basket[ k ]
      
    except KeyError:

      try:

        if s.parent:
          return s.parent[ k ]

      except KeyError:
        pass

      if s.hasDomain( k ):
        return s.getDomain( k )

      raise


  def __setitem__( s, attr, value ):
    
    attr = attr.lower().strip()

    if s.existsInParent( attr ) and s.parent[ attr ] == value:

      ## If the parent's value is already set to the new value, we delete
      ## the attribute on this object instead so we'll inherit that of its
      ## parent instead.

      try:
        del s[ attr ]

      except KeyError:
        pass

      return
 
    if s.exists( attr ) and s[ attr ] == value:

        ## If the value hasn't changed, we quit right away.
        return
 
    s.basket[ attr ] = value

    s.notifyKeyChanged( attr )


  def __delitem__( s, attr ):

    del s.basket[ attr ]

    s.notifyKeyChanged( attr )


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


  def getType( s, attr ):

    if s.types:
      return s.types.get( attr )

    if s.parent:
      return s.parent.getType( attr )

    else:
      return None


  def reset( s ):
  
    keys = s.basket.keys()

    s.basket.clear()

    for key in keys:
      s.notifyKeyChanged( key )


  def resetDomains( s ):
  
    s.domains.clear()

    s.notifyKeyChanged( s.SECTIONS )


  def owns( s, attr ):
  
    return s.basket.has_key( attr.lower().strip() )
    

  def existsInParent( s, attr ):

    if s.parent:
      return s.parent.exists( attr )

    return False


  def exists( s, attr ):

    return s.owns( attr ) or s.existsInParent( attr )


  def updateFromDict( s, d ):
    
    for k, v in d.iteritems():
      s[ k ] = v


  def getConfigUpdater( s ):
  
    return ConfigBasketUpdater( s )


  def isEmpty( s ):
  
    return len( s.basket ) == 0


  def hasDomain( s, domain ):

    return s.domains.has_key( domain )


  def getDomain( s, domain ):
    
    try:
      return s.domains[ domain ]
      
    except KeyError:
      raise KeyError( "This configuration object doesn't have a domain called " 
                    + "%s." % domain )


  def getDomainList( s ):

    return list( s.domains.iterkeys() )


  def saveDomain( s, domain, name ):

    domain.name = name
    domain.setParent( s )

    s.domains[ name ] = domain

    s.notifyKeyChanged( s.SECTIONS )


  def saveAsDomain( s, name ):

    ## Watch the difference with the above method: here, THIS object is being
    ## saved into its PARENT as a new domain.
    
    s.parent.saveDomain( s, name )


  def renameDomain( s, oldname, newname ):

    ## Warning: this function doesn't check whether the new domain name is
    ## already in use -- if so, that domain will be overridden. In other words,
    ## this is an 'mv' and not 'mv -i'.
    ## Code that makes use of this method should check that 'newname' is free,
    ## if it thinks it matters.

    domain = s.getDomain( oldname )  ## Will raise KeyError if no such domain.
    s.deleteDomain( oldname )
    domain.saveAsDomain( newname )

    s.notifyKeyChanged( s.SECTIONS )


  def deleteDomain( s, name ):
    
    try:
      del s.domains[ name ]
      
    except KeyError:
      raise KeyError( "This configuration object doesn't have a domain called "
                    + "%s." % domain )

    s.notifyKeyChanged( s.SECTIONS )


  def createAnonymousDomain( s ):
    
    return ConfigBasket( s )


  def createDomain( s, name ):
      
    c = s.createAnonymousDomain()
    c.saveAsDomain( name )
    return c


  def isAnonymous( s ):

    return s.name is None


  def getOwnDict( s ):

    return s.basket

  
  def dumpAsDict( s ):

    d = s.getOwnDict().copy()

    if s.domains:
      d[ s.SECTIONS ] = dict( [ ( name, s.domains[ name ].dumpAsDict() ) \
                                  for name in s.domains ] )
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
        s.saveDomain( ConfigBasket.buildFromDict( section ), name )

      del d[ ConfigBasket.SECTIONS ]
    
    s.updateFromDict( d )


  def notifyKeyChanged( s, key ):

    s.notifiers.triggerAll( key )

    for child in s.children:
      child.notifyKeyChanged( key )


  def registerNotifier( s, notifier ):

    s.notifiers.add( notifier )



## ---[ Class ConfigBasketUpdater ]------------------------------------

class ConfigBasketUpdater( ConfigBasket ):

  def commit( s ):
  
    s.parent.updateFromDict( s.basket )
    s.reset()



