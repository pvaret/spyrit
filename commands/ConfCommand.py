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
from Utilities   import format_as_table
from Defaults    import ALL_DESCS


class ConfCommand( BaseCommand ):

  u"Configure the application."

  def cmd_set( s, world, key, *args ):

    u"""\
    Sets the given configuration key to the given value.

    Usage: %(cmd)s <key> <value>

    Example: %(cmd)s output_font_name "Courier New"
    """

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )
      return

    args = t.from_string( args )
    singletons.config[ key ] = args

    value = t.to_string( args )
    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s set to value %s" % ( key, value ) )


  def cmd_worldset( s, world, key, *args ):

    u"""\
    Sets given configuration key to the given value, for this world only.

    Usage: %(cmd)s <key> <value>

    Example: %(cmd)s output_font_name "Courier New"
    """

    args = " ".join( args )

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )
      return

    args = t.from_string( args )
    world.conf[ key ] = args

    value = t.to_string( args )
    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s set to value %s on world %s" \
                % ( key, value, world.title() ) )


  def cmd_reset( s, world, key ):

    u"""\
    Resets the given configuration key to its default value.

    Usage: %(cmd)s <key>

    Example: %(cmd)s output_font_name
    """

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )
      return

    try:
      del singletons.config[ key ]

    except KeyError:
      pass

    value = t.to_string( singletons.config[ key ] )
    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s reset to value %s" % ( key, value ) )


  def cmd_worldreset( s, world, key ):

    u"""\
    Resets the given configuration key for this world to its global value.

    Usage: %(cmd)s <key>

    Example: %(cmd)s output_font_name
    """

    t = world.conf.getType( key )

    if not t:
      world.info( u"Unknown configuration key: %s" % key )
      return

    try:
      del world.conf[ key ]

    except KeyError:
      pass

    value = t.to_string( world.conf[ key ] )
    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s reset to value %s on world %s" \
                % ( key, value, world.title() ) )


  def cmd_keys( s, world ):

    u"""\
    Lists all available configuration keys.

    Usage: %(cmd)s
    """

    max_len = max( len( k ) for k in ALL_DESCS )

    output = u"Available configuration keys:\n"

    for key, desc in sorted( ALL_DESCS.iteritems() ):
      output += key.ljust( max_len + 2 )
      output += desc
      output += '\n'

    world.info( output )


  def cmd_show( s, world, key=None ):

    u"""\
    Show the current configuration.

    Usage: %(cmd)s [<key> | all]

    By default, only the values differing from defaults are shown.
    If an optional key argument is given, list all values for that key
    (default, global, world.)

    If the optional argument 'all' is given, then all values for all keys are
    listed.

    Example: %(cmd)s output_font_name
             %(cmd)s all
    """

    worldconf  = world.conf
    globalconf = singletons.config
    defaults   = globalconf.parent

    ## 1/ Retrieve list of keys to list, based on the argument given by the
    ## user:

    if key is not None:
      key = key.lower().strip()

    if key is None:  ## No argument given. Show non-default keys.

      list_keys = []

      for k in sorted( ALL_DESCS ):

        if worldconf.owns( k ) or globalconf.owns( k ):
          list_keys.append( k )

      if not list_keys:
        world.info( u"All the configuration keys have default values." )
        return

    elif key == "all":
      list_keys = sorted( ALL_DESCS )

    else:

      if defaults.getType( key ) is None:
        world.info( u"No such configuration key." )
        return

      list_keys = [ key ]


    ## 2/ Format and display as a table:

    output = "Current configuration:\n"

    headers = ( u"Keys", u"Defaults", u"Global", u"World" )

    columns = [ list_keys ]

    for conf in ( defaults, globalconf, worldconf ):

      column = []

      for k in list_keys:
        t = globalconf.getType( k )
        value = t.to_string( conf[ k ] ) if conf.owns( k ) else u"-"

        column.append( value if value else u"None" )

      columns.append( column )

    output += format_as_table( columns, headers )
    world.info( output )
