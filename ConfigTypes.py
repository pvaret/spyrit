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
## ConfigTypes.py
##
## Contains the configuration typing system: a set of classes for converting
## data from and to strings with a uniform interface and sane fallback
## defaults.
##


from FormatData import FORMAT_PROPERTIES


class INT:

  def from_string( s, i ):

    try:               return int( i )
    except ValueError: return 0


  def to_string( s, i ):

    return unicode( i )


class STR:

  def from_string( s, string ): return string

  def to_string( s, string ): return string



class BOOL:

  def from_string( s, b ):

    return b.lower() in ( u"1", u"y", u"yes", u"on", u"true" )
 

  def to_string( s, b ):

    return b and u"True" or u"False"


class INTLIST:

  def from_string( s, l ):

    result = []

    for token in l.split( u"," ):

      try:               result.append( int( token ) )
      except ValueError: pass

    return result


  def to_string( s, l ):

    return u",".join ( unicode( i ) for i in l )


def str_escape( s ):

  ESC = u'\\'
  ESC_CHARS = u'"' + u"'"

  result = []

  for c in s:
    result.append ( ( c == ESC or c in ESC_CHARS ) and ESC + c or c )

  return u"".join( result )


def split_on_unescaped_commas( s ):

  ESC    = u'\\'
  QUOTES = u'"' + u"'"
  COMMA  = u','

  current     = []
  in_escaped = False
  in_quotes  = u""  ## Evaluates as False.

  for c in s:

    if in_escaped:

      in_escaped = False
      current.append( c )

    else:

      if c == ESC:

        in_escaped = True
        continue
    
      if in_quotes:

        if c == in_quotes:  ## End of quoted string.
          in_quotes = u""

        current.append( c )

      else:

        if c == COMMA:

          yield u"".join ( current )
          current = []
          continue

        elif c in QUOTES:

          in_quotes = c

        current.append( c )

  yield u"".join( current )


class STRLIST:

  def to_string( s, l ):

    return u','.join( u'"' + str_escape( token ) + u'"' for token in l )


  def from_string( s, l ):

    QUOTES = u'"' + u"'"

    result = []

    for token in split_on_unescaped_commas( l ):

      if len( token ) >= 2:

        c = token[ 0 ]

        if c in QUOTES and token[ -1 ] == c:

          result.append( token[ 1:-1 ] )
          continue

      result.append( token )

    return result


class FORMAT:

  ## FORMAT describes the formatting for a given piece of text: color,
  ## italic, underlined...
  ## Its string serialization is a semicolon-separated list of tokens and
  ## looks like this: 'color:#ffffff; italic; bold'.
  ## Its deserialized form is a dictionary.
  ## We also store format-related constants on it.

  def to_string( s, d ):

    l = []

    for k, v in d.iteritems():

      if   k == FORMAT_PROPERTIES.COLOR:
        l.insert( 0, "color: %s" % v )

      elif k == FORMAT_PROPERTIES.ITALIC:
        l.append( "italic" )

      elif k == FORMAT_PROPERTIES.BOLD:
        l.append( "bold" )

      elif k == FORMAT_PROPERTIES.UNDERLINE:
        l.append( "underlined" )

    return " ; ".join( l )


  def from_string( s, l ):

    d = {}

    for item in l.split( ";" ):

      item  = item.strip().lower()
      value = None

      if ":" in item:

        item, value = item.split( ":", 1 )
        item  = item.strip()
        value = value.strip()

      if   item.startswith( "i" ):
        d[ FORMAT_PROPERTIES.ITALIC ] = True

      elif item.startswith( "b" ):
        d[ FORMAT_PROPERTIES.BOLD ] = True

      elif item.startswith( "u" ):
        d[ FORMAT_PROPERTIES.UNDERLINE ] = True

      elif item.startswith( "c" ):

        if value:
          d[ FORMAT_PROPERTIES.COLOR ] = value

    return d
