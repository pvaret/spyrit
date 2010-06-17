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
## HelpCommand.py
##
## Implements the good old help command.
##


from Singletons  import singletons
from BaseCommand import BaseCommand


class HelpCommand( BaseCommand ):

  def cmd( s, world, cmdname=None, subcmdname=None ):

    if cmdname:

      cmd = singletons.commands.lookupCommand( cmdname )

      if not cmd:
        return s.helpNoSuchCommand( world, cmdname )

      if subcmdname:
        subcmd = cmd.subcmds.get( subcmdname.strip().lower() )

        if not subcmd:
          return s.helpNoSuchCommand( world, cmdname, subcmdname )

        return s.helpSubCommand( world, subcmd, cmdname, subcmdname )

      return s.helpCommand( world, cmd, cmdname )

    return s.helpAll( world )


  def helpNoSuchCommand( s, world, cmdname, subcmdname=None ):
    pass ## TODO: implement


  def helpAll( s, world ):
    pass ## TODO: implement


  def helpCommand( s, world, cmd, cmdname ):
    pass ## TODO: implement


  def helpSubCommand( s, world, cmd, cmdname, subcmdname ):
    pass ## TODO: implement


  def get_short_help( s ):

    if s.__doc__:
      return s.__doc__.split( u"\n" )[0].strip()

    return None


  def get_help( s ):

    if not s.__doc__:
      return None

    doc = s.__doc__.strip()

    if not s.subcmds:
      return doc

    helptxt  = [ doc ]
    helptxt += [ u"" ]
    helptxt += [ u"Subcommands:" ]

    ljust = max( len( c ) for c in s.subcmds.keys() ) + 2

    for cmdname, cmd in sorted( s.subcmds.iteritems() ):

      doc = cmd.__doc__

      if doc:
        line = ( "  %s " % ( cmdname.ljust( ljust ) )
               + doc.split( u"\n" )[0].strip() )
        helptxt.append( line )

    return u"\n".join( helptxt )



  def doHelp( s, world, tokens ):

    tokens = tokens[ 1: ]

    ##XXX Improve whole help handling!

    if not tokens:  ## Default help text.

      helptxt = [ "Available commands:\n" ]

      ljust = max( len( c ) for c in s.commands.keys() ) + 2

      for cmdname in sorted( s.commands.keys() ):

        cmd  = s.lookupCommand( cmdname )
        help = cmd.get_short_help()

        if help:
          helptxt.append( CMDCHAR + u"%s" % cmdname.ljust( ljust ) + help )

      helptxt += [ "" ]
      helptxt += [ "Type '%shelp COMMAND' for more help on a command."
                   % CMDCHAR ]

      world.info( u'\n'.join( helptxt ) )

    else:  ## Help on a specific command.

      cmdname = tokens[0]
      cmd     = s.lookupCommand( cmdname )

      if not cmd:
        world.info( "No such command: %s" % cmdname )

      else:

        help = cmd.get_help()

        if not help:
          world.info( "No help for command %s. " \
                      "(Command reserved for internal use.)" % cmdname )
        else:
          world.info( CMDCHAR + u"%s " % cmdname + "\n  " + help )
