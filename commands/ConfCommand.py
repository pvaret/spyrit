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
## ConfCommand.py
##
## Commands to manage the configuration.
##


from BaseCommand import BaseCommand
from Singletons  import singletons


class ConfCommand( BaseCommand ):

  u"Configure the application."

  def cmd_set( s, world, key, *args ):

    u"Sets given configuration key to the given value globally."

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )

    else:
      args = t.from_string( args )
      singletons.config[ key ] = args


  def cmd_worldset( s, world, key, *args ):

    u"Sets given configuration key to the given value for this world."

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )

    else:
      args = t.from_string( args )
      world.conf[ key ] = args


  def cmd_reset( s, world, key ):

    u"Resets the given configuration key to its default value."

    try:
      del singletons.config[ key ]

    except KeyError:
      pass


  def cmd_worldreset( s, world, key ):

    u"Resets the given configuration key for this world to its global value."

    try:
      del world.conf[ key ]

    except KeyError:
      pass
