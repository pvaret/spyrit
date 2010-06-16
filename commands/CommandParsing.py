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
## CommandParsing.py
##
## Provides helpers to parse command lines.
##


import re

QUOTED = re.compile( ur'(\S*)' +
                     ur'(?:'   +
                       ur'"(.*?)"' + u'|' + ur"'(.*?)'" +
                     ur')'     +
                     ur'(\S*)' )

KWARG_SEP = u"="


def tokenize( line ):

  ## Turns a line such as '"A B" C="D E" F' into [ 'A B', 'C=D E', 'F' ]

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
      kwargs[ key ] = val

    else:
      args.append( token )

  return args, kwargs
