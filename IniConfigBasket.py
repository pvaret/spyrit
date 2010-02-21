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
## IniConfigBasket.py
##
## Implements a ConfigBasket subclass that can save itself as an INI file.
##


from Messages import messages


## ---[ function parseIniLine ]----------------------------------------

import re

RE_SECTION  = re.compile( r"^(\[+)(.+?)(\]+)(.*)", re.UNICODE )
RE_KEYVALUE = re.compile( r"^(\w(?:-*\w+)*)\s*=\s*(.*)", re.UNICODE )

def parseIniLine( line ):

  result = dict( key=u"", value=u"", section=u"", sectiondepth=0 )
  
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

from ConfigBasket import ConfigBasket


class IniConfigBasket( ConfigBasket ):

  ENCODING = "UTF-8"
  INDENT   = u"  "


  def __init__( s, filename, schema, autotypes=None ):

    s.filename = filename

    ConfigBasket.__init__( s, schema=schema, autotypes=autotypes )

    s.load()


  def load( s ):

    try:
      f = codecs.getreader( s.ENCODING ) ( open( s.filename ), "ignore" )

    except IOError:
      ## Unable to load configuration. Aborting.
      #messages.debug( u"Unable to load configuration file %s!" % s.filename )
      return

    s.reset()
    s.resetSections()

    currentconf  = s
    currentdepth = 0
    skipsection  = False

    for line in f:

      result = parseIniLine( line )
      if not result: continue

      key = result[ "key" ]

      if key and not skipsection:  ## This is a key/value line.

        t = currentconf.getType( key )

        if not t:

          messages.warn( u"Unknown configuration variable: %s" % key )
          continue

        value = t().from_string( result[ "value" ] )

        currentconf[ key ] = value

      elif result[ "section" ]:  ## This is a section line.

        skipsection = False

        depth = result[ "sectiondepth" ]

        if depth > currentdepth + 1:
          ## Okay, this subsection is too deep, i.e. it looks something like:
          ##   [[ some section ]]
          ##   ...
          ##    [[[[ some subsection ]]]]
          ## ... which is not good. So we skip it.
          skipsection = True
          continue

        while currentdepth >= depth:

          currentconf   = currentconf.parent
          currentdepth -= 1

        currentconf   = currentconf.createSection( result[ "section" ] )
        currentdepth += 1

    f.close()


  def save( s ):

    try:
      f = codecs.getwriter( s.ENCODING ) ( open( s.filename, "w" ), "ignore" )

    except IOError:
      ## Unable to save configuration. Aborting.
      messages.error( u"Unable to save configuration to file %s!" % s.filename )
      return

  
    def save_section( configobj, indent_level=0 ):

      for k, v in configobj.getOwnDict().iteritems():

        t = configobj.getType( k )

        if not t:  ## Unknown key!
          continue

        v = t().to_string( v )

        f.write( s.INDENT * indent_level )
        f.write( u"%s = %s\n" % ( k, v ) )

      for sectionname, section in configobj.sections.iteritems():

        if section.isEmpty():  ## Section is empty
          continue

        f.write( u"\n" )
        f.write( s.INDENT * indent_level )
        f.write( u"[" * ( indent_level + 1 ) )
        f.write( u" %s " % sectionname.strip() )
        f.write( u"]" * ( indent_level + 1 ) )
        f.write( u"\n" )

        save_section( section, indent_level+1 )

    save_section( s )

    f.close()
