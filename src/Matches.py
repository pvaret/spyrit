# -*- coding: utf-8 -*-

## Copyright (c) 2007-2015 Pascal Varet <p.varet@gmail.com>
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
## Matches.py
##
## The SmartMatch class handles pattern matching for triggers, highlighs and
## such, with a convenient interface for the user. It provides facilities to
## let the user enter their patterns in the following form:
##   '[player] pages: [message]'
## ... and generates the corresponding regex.
##
## The RegexMatch provides the same interface but uses actual regexes.
##


import re


class MatchCreationError( Exception ):
  pass


class RegexMatch:

  matchtype = u"regex"

  def __init__( self, pattern=u"" ):

    self.pattern = pattern
    self.regex   = None
    self.error   = None
    self.name    = None

    if pattern:
      self.setPattern( pattern )


  def compileRegex( self, regex ):

    self.error = None

    try:
      self.regex = re.compile( regex )

    except re.error, e:
      self.regex = re.compile( "$ ^" )  ## Clever regex that never matches.
      self.error = unicode( e )


  def setPattern( self, pattern ):

    self.pattern = pattern
    regex_pattern = self.patternToRegex( pattern )

    self.compileRegex( regex_pattern )


  def patternToRegex( self, pattern ):

    ## This is a regex match, so the regex IS the pattern.
    return pattern


  def matches( self, string ):

    if not self.regex:
      return None

    return list( self.regex.finditer( string ) )


  def matchtokens( self ):

    if not self.regex:
      return None

    tokens = sorted( [ ( v, k ) for k, v in self.regex.groupindex.iteritems() ] )

    return [ tok[1] for tok in tokens ]


  def __repr__( self ):

    return self.matchtype + u':' + self.pattern


  def __unicode__( self ):

    return u"'" + self.pattern + u"' (regex)"




## This convoluted regex parses out either words (\w+) between square brackets
## or asterisks, if they aren't preceded by an odd number of backslashes.


TOKEN = ur' *\w+ *' ## Non-null word with optional surrounding space.

BS      = ur'\\' ## Backslash
ASTER   = ur'\*' ## Asterisk
PERCENT = ur'\%' ## Percent sign

LSB   = ur'\[' ## Left square bracket
RSB   = ur'\]' ## Right square bracket

PARSER = re.compile(
    u'(?:'                      ## Either...
  +   u'^'                      ## Beginning of string
  + u'|'                        ## Or...
  +   u'[^' + BS + u']'         ## Any one character other than a backslash
  + u')'                        ## Then...
  + u'(?:' + BS * 2 + u')'
  + u'*'                        ## An even number of backslashes
  + u'('                        ## And then, group-match either...
  +    PERCENT                  ## A percent sign
  + u'|'                        ## Or...
  +    ASTER                    ## An asterisk
  + u'|'                        ## Or...
  +    LSB
  +      TOKEN                  ## Something of the form [token].
  +    RSB
  + u')'
)


class SmartMatch( RegexMatch ):

  matchtype = u"smart"

  def patternToRegex( self, pattern ):

    regex  = []
    tokens = set()

    while pattern:

      m = PARSER.search( pattern )

      if not m:

        regex.append( self.unescape_then_escape( pattern ) )
        break

      start, end = m.span( 1 )
      before, pattern = pattern[ :start ], pattern[ end: ]

      if before:
        regex.append( self.unescape_then_escape( before ) )

      token = m.group( 1 ).lower().lstrip( u'[ ' ).rstrip( u' ]' )

      if token == u'%':
        regex.append( u".*?" ) ## Match anything, non-greedy

      elif token == u'*':
        regex.append( u".*" )  ## Match anything, greedy

      elif token in tokens:  ## Token which is already known
        regex.append( u"(?P=%s)" % token ) ## Insert backreference.

      else:  ## New token
        tokens.add( token )

        ## Named match for any non-null string, non-greedy.
        regex.append( ur"(?P<%s>.+?)" % token )

    return u''.join( regex )


  def unescape_then_escape( self, string ):

    ## Unescape string according to the SmartMatch parser's rules, then
    ## re-escape according to the rules of Python's re module.

    replacements = (
      ( u"\[",   u"[" ),
      ( u"\]",   u"]" ),
      ( u"\*",   u"*" ),
      ( u"\\"*2, u"\\" ),
    )

    for from_, to in replacements:
      string = string.replace( from_, to )

    return re.escape( string )


  def __unicode__( self ):

    return u"'" + self.pattern + u"'"



def load_match_by_type( pattern, type=u"smart" ):

  type = type.lower().strip()

  TYPES = {
    u"smart": SmartMatch,
    u"regex": RegexMatch,
  }

  klass = TYPES.get( type )

  if not klass:
    raise MatchCreationError( u"Unknown match type: %s" % type )

  match = klass( pattern )

  if match.error:
    raise MatchCreationError( u"Match pattern syntax error: %s" % match.error )

  return match
