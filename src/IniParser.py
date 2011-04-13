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
## IniConfigBasket.py
##
## Implements a ConfigBasket subclass that can save itself as an INI file.
##

u"""
:doctest:

>>> from IniParser import *

"""


import re

RE_SECTION  = re.compile( r"^(\[+)(.+?)(\]+)(.*)", re.UNICODE )
RE_KEYVALUE = re.compile( r"^(\w(?:-*\w+)*)\s*=\s*(.*)", re.UNICODE )

INDENT   = u"  "


def parse_ini_line( line ):

  result = dict( key=u"", value=u"", section=u"", sectiondepth=0 )

  line = line.strip()

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



def ini_to_struct( ini_text ):
  u"""
  Parses an ini-formatted block of text into a programmatically usable
  structure.

  >>> from pprint import pprint
  >>> pprint( ini_to_struct( ur'''
  ...
  ... key1 = 1
  ... key2 = 2
  ...
  ... [ section1 ]
  ...
  ...   [[ subsection1 ]]
  ...     key3 = "This is a string"
  ...
  ...     [[[[ wrong_depth ]]]]
  ...       key4 = "Section has wrong depth and will be ignored"
  ...
  ... [ section2 ]
  ...   key5 = 5
  ...
  ... ''' ) )  #doctest: +NORMALIZE_WHITESPACE
  ({u'key1': u'1', u'key2': u'2'},
   {u'section1': ({},
                  {u'subsection1': ({u'key3': u'"This is a string"'},
                                    {})}),
    u'section2': ({u'key5': u'5'}, {})})

  """

  KEYS, SECTIONS = 0, 1

  struct = ( {}, {} )  ## keys, subsections
  current_struct = struct

  struct_stack = []

  skipsection  = False

  for line in ini_text.split( u'\n' ):

    result = parse_ini_line( line )

    if not result:
      continue

    key     = result[ "key" ]
    section = result[ "section" ]

    if key and not skipsection:  ## This is a key/value line.

      current_struct[ KEYS ][ key ] = result[ "value" ]

    elif section:  ## This is a section line.

      skipsection = False

      depth = result[ "sectiondepth" ]

      if depth > len( struct_stack ) + 1:
        ## Okay, this subsection is too deep, i.e. it looks something like:
        ##   [[ some section ]]
        ##   ...
        ##    [[[[ some subsection ]]]]
        ## ... which is not good. So we skip it.
        skipsection = True
        continue

      while len( struct_stack ) >= depth:
        current_struct = struct_stack.pop()

      current_struct[ SECTIONS ][ section ] = ( {}, {} )
      struct_stack.append( current_struct )
      current_struct = current_struct[ SECTIONS ][ section ]

  return struct




def struct_to_ini( struct, depth=0 ):

  """Takes a programmatic structure and generates an INI representation for it.

  The structure is a tuple of the form ( keys, sections ), where 'keys' and
  'sections' are both dictionaries. 'keys' associates setting names to values,
  both expressed as strings, and section associates section names to
  sub-structures of the same type as the parent structure.

  >>> keys = { u'key1': u"1", u'key2': "2" }
  >>> sections = { 'subsection': ( { u'otherkey': u'3' }, {} ) }
  >>> print struct_to_ini( ( keys, sections ) )
  key1 = 1
  key2 = 2
  <BLANKLINE>
    [ subsection ]
    otherkey = 3
  <BLANKLINE>

  """

  output = u''

  keys, sections = struct

  for k, v in sorted( keys.iteritems() ):
    output += "%s%s = %s\n" % ( INDENT*depth, k, v )

  depth += 1

  for k, substruct in sorted( sections.iteritems() ):
    output += u'\n'
    output += INDENT * depth
    output += u'[' * depth
    output += u' %s ' % k
    output += u']' * depth
    output += u'\n'
    output += struct_to_ini( substruct, depth )

  return output
