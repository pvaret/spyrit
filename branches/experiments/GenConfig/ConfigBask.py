##
## GenConfig.py
##
## Holds the classes that handle the configuration subsystem.
##




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
  
    if len( attr ) > 2 \
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



## ---[ Class CoreConfigBasket ]---------------------------------------

class CoreConfigBasket( object ):
  """
  CoreConfigBasket( object )
  
  This class holds the core behavior for a set of configuration keys.
  """

  __metaclass__ = MetaDictProxy



  def __init__( s, parent=None ):

    s.name   = None
    s.basket = {}
    s.realms = {}
    s.parent = parent


  def __getitem__( s, k ):

    try:
      return s.basket[ k ]
      
    except KeyError:

      try:

        if s.parent:
          return s.parent[ k ]

      except KeyError:
        pass

      if s.hasRealm( k ):
        return s.getRealm( k )

      raise


  def __setitem__( s, attr, value ):
    
 
    ## If the parent already has this configuration key AND its value
    ## is the same, then we can safely delete it from the child
    ## configuration object, since the value can then be inherited
    ## from the parent.
    if s.parent and \
      s.parent.exists( attr ) and \
      value == s.parent[ attr ]:
      
      try:
        del s.basket[ attr ]
        
      except KeyError:
        pass

    else:
      s.basket[ attr ] = value


  def __delitem__( s, attr ):

    del s.basket[ attr ]


  def reset( s ):
  
    s.basket.clear()


  def owns( s, attr ):
  
    return s.basket.has_key( attr )
    

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


  def hasRealm( s, realm ):

    return s.realms.has_key( realm )


  def getRealm( s, realm ):
    
    try:
      return s.realms[ realm ]
      
    except KeyError:
      raise KeyError( "This configuration object doesn't have a realm called %s." % realm )


  def saveRealm( s, realm, name ):

    s.realms[ name ] = realm


  def saveAsRealm( s, name ):

    ## Watch the difference with the above method: here, THIS object is being
    ## saved into its PARENT as a new realm.
    
    s.name = name
    s.parent.saveRealm( s, name )


  def deleteRealm( s, name ):
    
    try:
      del s.realms[ name ]
      
    except KeyError:
      raise KeyError( "This configuration object doesn't have a realm called %s." % realm )


  def createAnonymousRealm( s ):
    
    return CoreConfigBasket( s )


  def createRealm( s, name ):
      
    c = s.createAnonymousRealm()
    c.saveAsRealm( name )
    return c


  def getOwnDict( s ):

    return s.basket

  
  def getAllDataAsDict( s ):

    d = dict( s.getOwnDict().copy() )
    d[ "_sections" ] = dict( [ ( name, realm.getAllDataAsDict() ) \
                                 for ( name, realm ) in s.realms.iteritems() ] )
    return d



## ---[ Class ConfigBasket ]-------------------------------------------

class ConfigBasket( CoreConfigBasket ):

  def __init__( s ):

    CoreConfigBasket.__init__( s )
    
    s.specs  = None
    s.loader = None
    s.saver  = None


  def save( s ):
    
    if not s.saver:
      raise TypeError( "This configuration object has no saver." )

    pass #XXX



  def load( s ):

    if not s.loader():
      raise TypeError( "This configuration object has no loader." )

    pass #XXX




## ---[ Class ConfigBasketUpdater ]------------------------------------

class ConfigBasketUpdater( CoreConfigBasket ):

  def __init__( s, parent ):
  
    CoreConfigBasket.__init__( s, parent )


  def commit( s ):
  
    s.parent.updateFromDict( s.basket )
    s.reset()



