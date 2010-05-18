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




class RegexMatch:

  matchtype = "regex"

  def __init__( s, pattern=None ):

    s.pattern   = pattern
    s.regex     = None
    s.result    = None
    s.error     = None
    s.name      = None

    if pattern:
      s.setPattern( pattern )


  def compileRegex( s, regex ):

    s.result = None
    s.error  = None

    try:
      s.regex = re.compile( regex )

    except re.error, e:
      s.regex = re.compile( "$ ^" )  ## Clever regex that never matches.
      s.error = e.message


  def setPattern( s, pattern ):

    s.pattern     = pattern
    regex_pattern = s.patternToRegex( pattern )

    s.compileRegex( regex_pattern )


  def patternToRegex( s, pattern ):

    return pattern


  def matches( s, string ):

    s.result = None

    if not s.regex:
      return False

    m = s.regex.search( string )

    if m is None:  ## Doesn't match.
      return False

    s.result = m

    return True


  def matchtokens( s ):

    if not s.regex:
      return None

    tokens = sorted( [ ( v, k ) for k, v in s.regex.groupindex.iteritems() ] )

    return [ tok[1] for tok in tokens ]


  def __unicode__( s ):

    return u":".join( [ s.matchtype, s.pattern ] )




## This convoluted regex parses out either words (\w+) between square brackets
## or asterisks, if they aren't preceded by an odd number of backslashes.


TOKEN = r" *\w+ *" ## Non-null word with optional surrounding space.

BS      = r"\\" ## Backslash
ASTER   = r"\*" ## Asterisk
PERCENT = r"\%" ## Percent sign

LSB   = r"\[" ## Left square bracket
RSB   = r"\]" ## Right square bracket

PARSER = re.compile(
    "(?:"                      ## Either...
  +   "^"                      ## Beginning of string
  + "|"                        ## Or...
  +   "[^" + BS + "]"          ## Any one character other than a backslash
  + ")"                        ## Then...
  + "(?:" + BS * 2 + ")"
  + "*"                        ## An even number of backslashes
  + "("                        ## And then, group-match either...
  +   PERCENT                  ## A percent sign
  + "|"                        ## Or...
  +   ASTER                    ## An asterisk
  + "|"                        ## Or...
  +   LSB
  +     TOKEN                  ## Something of the form [token].
  +   RSB
  + ")"
)


class SmartMatch( RegexMatch ):

  matchtype = "smart"

  def patternToRegex( s, pattern ):

    regex  = []
    tokens = set()

    while pattern:

      m = PARSER.search( pattern )

      if not m:

        regex.append( s.unescape_then_escape( pattern ) )
        break

      start, end = m.span( 1 )
      before, pattern = pattern[ :start ], pattern[ end: ]

      if before:
        regex.append( s.unescape_then_escape( before ) )

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
        regex.append( ur"\b(?P<%s>.+?)\b" % token )

    return u''.join( regex )


  def unescape_then_escape( s, string ):

    ## Unescape string according to the SmartMatch parser's rules, then
    ## re-escape according to the rules of Python's re module.

    replacements = (
      ( "\[",   "[" ),
      ( "\]",   "]" ),
      ( "\*",   "*" ),
      ( "\\"*2, "\\" ),
    )

    for from_, to in replacements:
      string = string.replace( from_, to )

    return re.escape( string )





def load_from_string( string ):

  if string.startswith( "regex:" ):
    return RegexMatch( string[ 6: ] )

  if string.startswith( "smart:" ):
    return SmartMatch( string[ 6: ] )

  return SmartMatch( string )