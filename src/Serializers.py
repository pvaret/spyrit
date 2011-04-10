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
## Serializers.py
##
## Serializers are small classes that know how to serialize and deserialize
## configuration values to and from strings, and can also compute and retain a
## sane default for each given configuration key.
##

u"""
:doctest:

>>> from Serializers import *

"""


from PyQt4.QtGui  import QKeySequence
from PyQt4.QtCore import QSize, QPoint

from Globals   import FORMAT_PROPERTIES
from Matches   import RegexMatch, SmartMatch
from Utilities import quote, unquote, BS




def split( string, sep=u',', esc=BS, quotes=u'"'+u"'" ):
  ur"""
  Splits a string along the given single-character separator (by default, a
  comma).

  Only split if the separator is not escaped or inside a quoted section.

  >>> print len( list( split( u' "A", "B" ' ) ) )
  2

  >>> print len( list( split( ur' "A"\, "B" ') ) )
  1

  >>> print len( list( split( u' "A, B" ') ) )
  1

  """

  last_pos      = 0
  in_escape     = False
  current_quote = None

  for pos, c in enumerate( string ):

    if in_escape:
      ## Current character is escaped. Move on.
      in_escape = False
      continue

    if c == esc:
      ## Next character will be escaped.
      in_escape = True
      continue

    if current_quote is None:
      ## Not in a quoted section.

      if c == sep:
        ## Found an unquoted separator! Split.
        yield string[ last_pos:pos ]
        last_pos = pos + 1  ## Skip the separator itself.

      elif c in quotes:
        ## This is the start of a quoted section.
        current_quote = c

      continue

    ## In a quoted section. Do nothing until the section ends.

    if c == current_quote:
      ## This is the end of the quoted section.
      current_quote = None

  if last_pos < len( string ):
    yield string[ last_pos: ]





class BaseSerializer:

  def __init__( self, default=None ):

    self.default = self.deserialize( default ) if default is not None else None


  def serialize( self, value ):

    raise NotImplementedError( "Serializers must implement the serialize method." )


  def deserialize( self, string ):

    raise NotImplementedError( "Serializers must implement the deserialize method." )



class Int( BaseSerializer ):

  def deserialize( self, string ):

    try:
      return int( string )

    except ValueError:
      return 0


  def serialize( self, int_ ):

    if isinstance( int_, int ):
      return unicode( int_ )

    return u''


class Str( BaseSerializer ):

  def deserialize( self, string ):

    return unquote( string )


  def serialize( self, string ):

    return quote( string )



class Bool( BaseSerializer ):

  def deserialize( self, string ):

    return string.strip().lower() in ( u"1", u"y", u"yes", u"on", u"true" )


  def serialize( self, bool_ ):

    return u"True" if bool_ else u"False"


class List( BaseSerializer ):

  sep = u","

  def __init__( self, sub_serializer, default=None ):

    self.sub_serializer = sub_serializer
    BaseSerializer.__init__( self, default )


  def serialize( self, list_ ):

    return self.sep.join( self.sub_serializer.serialize( item )
                          for item in list_ )

  def deserialize( self, string ):

    return list( self.sub_serializer.deserialize( item )
                 for item in split( string, sep=self.sep ) )



class Format( BaseSerializer ):

  ## FORMAT describes the formatting for a given piece of text: color,
  ## italic, underlined...
  ## Its string serialization is a semicolon-separated list of tokens and
  ## looks like this: 'color:#ffffff; italic; bold'.
  ## Its deserialized form is a dictionary.
  ## We also store format-related constants on it.

  def serialize( self, d ):

    l = []

    for k, v in d.iteritems():

      if   k == FORMAT_PROPERTIES.COLOR:
        l.insert( 0, u"color: %s" % v )

      elif k == FORMAT_PROPERTIES.ITALIC:
        l.append( u"italic" )

      elif k == FORMAT_PROPERTIES.BOLD:
        l.append( u"bold" )

      elif k == FORMAT_PROPERTIES.UNDERLINE:
        l.append( u"underlined" )

    return u" ; ".join( l )


  def deserialize( self, l ):

    d = {}

    for item in l.split( u";" ):

      item  = item.strip().lower()
      value = None

      if u":" in item:

        item, value = item.split( u":", 1 )
        item  = item.strip()
        value = value.strip()

      if   item.startswith( u"i" ):
        d[ FORMAT_PROPERTIES.ITALIC ] = True

      elif item.startswith( u"b" ):
        d[ FORMAT_PROPERTIES.BOLD ] = True

      elif item.startswith( u"u" ):
        d[ FORMAT_PROPERTIES.UNDERLINE ] = True

      elif item.startswith( u"c" ):

        if value:
          d[ FORMAT_PROPERTIES.COLOR ] = value

    return d



class KeySequence( BaseSerializer ):

  def __init__( self, default=None ):

    ## QKeySequence.fromString uses PortableText by default, and so do our
    ## defaults:
    self.default = QKeySequence.fromString( default ) if default is not None \
                   else None


  def serialize( self, seq ):

    if seq is not None:
      return unicode( seq.toString( QKeySequence.NativeText) )

    return u""


  def deserialize( self, string ):

    return QKeySequence.fromString( string, QKeySequence.NativeText )


class Size( BaseSerializer ):

  def serialize( self, size ):

    return u"%dx%d" % ( size.width(), size.height() )


  def deserialize( self, string ):

    string = string.lower().strip()

    if u'x' in string:

      w, h = string.split( u'x', 1 )

      try:
        return QSize( int( w ), int( h ) )

      except TypeError:
        pass

    return QSize()


class Point( BaseSerializer ):

  def serialize( self, point ):

    return u"%dx%d" % ( point.x(), point.y() )


  def deserialize( self, string ):

    string = string.lower().strip()

    if u'x' in string:

      x, y = string.split( u'x', 1 )

      try:
        return QPoint( int( x ), int( y ) )

      except TypeError:
        pass

    return QPoint()


class Pattern( BaseSerializer ):

  def serialize( self, pattern ):

    if any( isinstance( pattern, cls ) for cls in ( RegexMatch, SmartMatch) ):
      return repr( pattern )

    return u''


  def deserialize( self, string ):

    if u":" in string:

      prefix, suffix = string.split( u":", 1 )
      prefix = prefix.lower()

      for cls in ( RegexMatch, SmartMatch ):

        if prefix == cls.matchtype:
          return cls( suffix )

    return SmartMatch( string )
