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
## SmartMatch.py
##
## The SmartMatch class handles pattern matching for triggers, highlighs and
## such, with a convenient interface for the user. It provides facilities to
## let the user enter their patterns in the following form:
##   '[player] pages: [message]'
## ... and generates the corresponding regex.
##


import re


## This convoluted regex parses out either words (\w+) between square brackets
## or asterisks, if they aren't preceded by an odd number of backslashes.


TOKEN = r" *\w+ *" ## Non-null word with optional surrounding space.

BS    = r"\\" ## Backslash
ASTER = r"\*" ## Asterisk

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
  +   ASTER                    ## An asterisk
  + "|"                        ## Or...
  +   LSB
  +     TOKEN                  ## Something of the form [token].
  +   RSB
  + ")"
)



class SmartMatch:

  def __init__( s ):

    s.pattern   = None
    s.regex     = None
    s.results   = None
    s.positions = None
    s.error     = None
    

  def setRegex( s, regex ):

    s.pattern = None
    s.compileRegex( regex )


  def compileRegex( s, regex ):

    s.clearResults()
    s.error = None

    try:
      s.regex = re.compile( regex )

    except re.error, e:
      s.regex = re.compile( "$ ^" )  ## Clever regex that never matches.
      s.error = e.message
    

  def setPattern( s, pattern ):

    s.pattern = pattern
    s.clearResults()
    s.parsePattern()


  def unescape_then_escape( s, string ):

    replacements = (
      ( "\[",   "[" ),
      ( "\]",   "]" ),
      ( "\*",   "*" ),
      ( "\\"*2, "\\" ),
    )

    for from_, to in replacements:
      string = string.replace( from_, to )

    return re.escape( string )


  def parsePattern( s ):

    pattern = s.pattern
    regex   = []
    tokens  = []

    while pattern:

      m = PARSER.search( pattern )

      if not m:

        regex.append( s.unescape_then_escape( pattern ) )
        break

      start, end = m.start( 1 ), m.end( 1 )
      before, pattern = pattern[ :start ], pattern[ end: ]

      if before:
        
        regex.append( s.unescape_then_escape( before ) )

      token = m.group( 1 ).lstrip( u'[ ' ).rstrip( u' ]' )

      if token == u'*':
        regex.append( u".*?" ) ## Match anything, non-greedy

      elif token in tokens:  ## Token is already known!

        regex.append( u"(?P=%s)" % token ) ## Insert backreference.

      else:

        tokens.append( token )
        #regex.append( ur"(?P<%s>\b.+\b)" % token )
        regex.append( u"(?P<%s>.+)" % token )

    s.compileRegex( u''.join( regex ) )


  def matches( s, string ):

    if not s.regex: return False

    m = s.regex.match( string )

    if m is None:  ## Doesn't match.

      s.clearResults()
      return False

    s.results = m.groupdict()

    s.positions = [ ( m.start( token ), m.end( token ), token )
                    for token in s.matchnames() ]

    return True


  def matchnames( s ):

    if not s.regex: return None

    matchnames = sorted( [ ( v, k )
                           for k, v in s.regex.groupindex.iteritems() ] )

    return [ m[1] for m in matchnames ]


  def clearResults( s ):

    s.results   = None
    s.positions = None
