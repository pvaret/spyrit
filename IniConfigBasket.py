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
## IniConfigBasket.py
##
## Implements a ConfigBasket subclass that can save itself as an INI file.
##


import re
import codecs

from Messages         import messages
from ConfigBasket     import ConfigBasket
from CallbackRegistry import CallbackRegistry



## ---[ function parseIniLine ]----------------------------------------


RE_SECTION  = re.compile( r"^(\[+)(.+?)(\]+)(.*)", re.UNICODE )
RE_KEYVALUE = re.compile( r"^(\w(?:-*\w+)*)\s*=\s*(.*)", re.UNICODE )

def parseIniLine( line ):

  result = dict( key=u"", value=u"", section=u"", sectiondepth=0 )

  line=line.strip()

  if line and line[ 0 ] in ( '#', ';' ):  ## Line is a comment.
    return None

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

class IniConfigBasket( ConfigBasket ):

  ENCODING = "UTF-8"
  INDENT   = u"  "


  def __init__( s, defaults, types ):

    ConfigBasket.__init__( s )

    d = ConfigBasket.buildFromDict( defaults )
    d.setTypeGetter( types.get )

    s.setParent( d )

    s.aboutToSave = CallbackRegistry()


  def load( s, filename ):

    try:
      f = codecs.getreader( s.ENCODING ) ( open( filename ), "ignore" )

    except IOError:
      ## Unable to load configuration. Aborting.
      #messages.debug( u"Unable to load configuration file %s!" % filename )
      return

    s.reset()
    s.resetSections()

    currentconf  = s
    currentdepth = 0
    skipsection  = False

    for line in f:

      result = parseIniLine( line )
      if not result:
        continue

      key = result[ "key" ]

      if key and not skipsection:  ## This is a key/value line.

        t = currentconf.getType( key )

        if not t:

          messages.warn( u"Unknown configuration variable: %s" % key )
          continue

        value = t.from_string( result[ "value" ] )

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


  def save( s, filename ):

    s.aboutToSave.triggerAll()

    config_txt = []
    config_txt.append( u"## version: 1\n" )

    def save_section( configobj, indent_level=0 ):

      for k, v in configobj.getOwnDict().iteritems():

        t = configobj.getType( k )

        if not t:  ## Unknown key!
          continue

        v = t.to_string( v )

        config_txt.append( s.INDENT * indent_level )
        config_txt.append( u"%s = %s\n" % ( k, v ) )

      for sectionname, section in configobj.sections.iteritems():

        if section.isEmpty():  ## Section is empty
          continue

        config_txt.append( u"\n" )
        config_txt.append( s.INDENT * indent_level )
        config_txt.append( u"[" * ( indent_level + 1 ) )
        config_txt.append( u" %s " % sectionname.strip() )
        config_txt.append( u"]" * ( indent_level + 1 ) )
        config_txt.append( u"\n" )

        save_section( section, indent_level+1 )

    save_section( s )

    try:
      f = codecs.getwriter( s.ENCODING ) ( open( filename, "w" ), "ignore" )

    except IOError:
      ## Unable to save configuration. Aborting.
      messages.error( u"Unable to save configuration to file %s!" % filename )
      return

    f.write( ''.join(  config_txt ) )

    f.close()


  def registerSaveCallback( s, callback ):

    s.aboutToSave.add( callback )
