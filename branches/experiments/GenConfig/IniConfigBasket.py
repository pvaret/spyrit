##
## IniConfigBasket.py
##
## Implements a ConfigBasket subclass that can save itself as an INI file.
##




## ---[ Class IniConfigBasket ]----------------------------------------

from ConfigBasket import ConfigBasket

class IniConfigBasket( ConfigBasket ):

  ENCODING = "utf-8"
  INDENT   = "  "


  def __init__( s, filename ):

    s.filename=filename
    ConfigBasket.__init__( s )


  def load( s ):

    try:
      f = open( s.filename )

    except IOError:
      ## Unable to load configuration. Aborting.
      return

    s.reset()
    s.resetRealms()

    data={}

    for line in f:
      raise Exception("XXX TO BE IMPLEMENTED")

    s.updateFromDictTree( data )

    f.close()


  def save( s ):

    try:
      f = file( s.filename, "w" )

    except IOError:
      ## Unable to save configuration. Aborting.
      return
      
    from demjson import JSON
    json = JSON( strict=True, escape_unicode=False )


    def save_section( basketdump, indent_level=0 ):

      subsections = None

      for k, v in basketdump.iteritems():

        if k == ConfigBasket.SECTIONS:
          subsections = v

        else:
          f.write( s.INDENT * indent_level )
          f.write( "%s = %s\n" % ( k, json.encode( v ) ) )

      if subsections:

        indent_level += 1

        for sectionname, sectiondata in subsections.iteritems():

          if type( sectionname ) is type( u"" ): ## Unicode
            sectionname = sectionname.encode( s.ENCODING )

          f.write( "\n" )
          f.write( s.INDENT * indent_level )
          f.write( "[" * indent_level )
          f.write( "%s" % sectionname.strip() )
          f.write( "]" * indent_level )
          f.write( "\n" )

          save_section( sectiondata, indent_level )

    save_section( s.dumpAsDict() )

    f.close()
