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
## CommandParsing.py
##
## Provides helpers to parse command lines.
##

u"""
:doctest:

>>> from commands.CommandParsing import *

"""


import re

QUOTED = re.compile( ur'([^"\'\s]*)' +     ## Anything but space or quote
                     ur'(?:'         +     ## Non-grouping match...
                       ur'"(.*?)"' + u'|' + ur"'(.*?)'" +  ## Anything quoted
                     ur')'           +
                     ur'([^"\'\s]*)' )     ## Anything but space or quote

KWARG_SEP = u"="


def tokenize( line ):
  u"""\
  Split a line of text into a list of tokens, respecting quotes.

  >>> print tokenize('''   "A B" C="D 'E'" F   ''')
  ['A B', "C=D 'E'", 'F']

  Does the right thing even in complex cases:

  >>> print tokenize('''   '' "''" "'"   ''')
  ['', "''", "'"]

  """

  line   = line.strip()
  tokens = []

  while True:

    m = QUOTED.search( line )

    if m:

      for token in line[ 0:m.start() ].split():
        tokens.append( token.strip() )

      token  = m.group( 1 )
      token += m.group( 2 ) if m.group( 2 ) is not None else m.group( 3 )
      token += m.group( 4 )

      tokens.append( token )

      line = line[ m.end(): ]

    else:

      for token in line.split():
        tokens.append( token.strip() )

      break

  return tokens


def parse_command( cmdline ):

  ## For now, a simple split will do.

  cmdline = cmdline.strip()

  if cmdline:
    cmd = cmdline.split()[0]
    return cmd, cmdline[ len( cmd ): ]

  return "", cmdline


def parse_arguments( cmdline ):

  args   = []
  kwargs = {}

  tokens = tokenize( cmdline )

  for token in tokens:

    if KWARG_SEP in token:

      key, val = token.split( KWARG_SEP, 1 )

      ## WORKAROUND: Some versions of Python break on Unicode keyword
      ## arguments. So encode them safely into bytestrings.
      if isinstance( key, unicode ):
        key = key.encode( 'utf-8' )

      kwargs[ key ] = val

    else:
      args.append( token )

  return args, kwargs
