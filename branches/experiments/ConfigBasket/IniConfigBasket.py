##
## IniConfigBasket.py
##
## Implements a ConfigBasket subclass that can save itself as an INI file.
##


## ---[ function parseIniLine ]----------------------------------------

import re

RE_SECTION  = re.compile( r"^(\[+)(.+?)(\]+)(.*)" )
RE_KEYVALUE = re.compile( r"^(\w+)\s*=\s*(.*)" )
RE_QUOTED_STRING = re.compile( r'^(".*[^\\](\\\\)*").*' )

def parseIniLine( line ):

  result = dict( key="", value="", section="", sectiondepth=0 )
  
  line=line.strip()

  m = RE_SECTION.match( line )

  if m:
    result[ "section" ]      = m.group( 2 ).strip()
    result[ "sectiondepth" ] = len( m.group( 1 ) )
    return result

  m = RE_KEYVALUE.match( line )

  if m:
    result[ "key" ]   = m.group( 1 )
    result[ "value" ] = m.group( 2 ).strip()
    return result
        
  return None
  

## ---[ Class IniConfigBasket ]----------------------------------------

import codecs
import demjson
from ConfigBasket import ConfigBasket

class IniConfigBasket( ConfigBasket ):

  ENCODING = "utf-8"
  INDENT   = "  "


  def __init__( s, filename ):

    s.filename=filename
    ConfigBasket.__init__( s )


  def load( s ):

    try:
      f = codecs.getreader( s.ENCODING ) ( open( s.filename ), "ignore" )

    except IOError:
      ## Unable to load configuration. Aborting.
      return

    s.reset()
    s.resetDomains()

    json = demjson.JSON()

    data        = {}
    currentdict = data
    currentpath = []
    skipsection = False

    for line in f:

      result = parseIniLine( line )
      if not result: continue

      if result[ "key" ] and not skipsection:

        try:
          value = json.decode( result[ "value" ] )

        except demjson.JSONDecodeError:
          ## Error in the line. We carry on.
          continue

        currentdict[ result[ "key" ] ] = value

      elif result[ "section" ]:

        skipsection = False
        depth       = result[ "sectiondepth" ]

        if depth > len( currentpath ) + 1:
          ## Okay, this subsection is too deep, i.e. it looks something like:
          ##   [[ some section ]]
          ##   ...
          ##    [[[[ some subsection ]]]]
          ## ... which is not good. So we skip it.
          skipsection = True
          continue

        section     = result[ "section" ]
        currentdict = data
        currentpath = currentpath[ :depth-1 ]

        for subsection in currentpath:
          currentdict = currentdict[ ConfigBasket.SECTIONS ][ subsection ]

        if ConfigBasket.SECTIONS not in currentdict:
          currentdict[ ConfigBasket.SECTIONS ] = {}

        if section not in currentdict[ ConfigBasket.SECTIONS ]:
          currentdict[ ConfigBasket.SECTIONS ][ section ] = {}        

        currentdict = currentdict[ ConfigBasket.SECTIONS ][ section ]
        currentpath.append( section )

     ## Phew, done.

    f.close()
    s.updateFromDictTree( data )


  def save( s ):

    try:
      f = file( s.filename, "w" )

    except IOError:
      ## Unable to save configuration. Aborting.
      return
      
    json = demjson.JSON( strict=True, escape_unicode=False )


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
          f.write( s.INDENT * ( indent_level-1 ) )
          f.write( "[" * indent_level )
          f.write( "%s" % sectionname.strip() )
          f.write( "]" * indent_level )
          f.write( "\n" )

          save_section( sectiondata, indent_level )

    save_section( s.dumpAsDict() )

    f.close()
