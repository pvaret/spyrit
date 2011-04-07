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
## SettingsCommand.py
##
## Commands to manage the configuration.
##


from PyQt4.QtGui import QApplication

from Settings    import SETTINGS_LABEL
from Utilities   import format_as_table
from BaseCommand import BaseCommand


class SettingsCommand( BaseCommand ):

  u"View and modify the application settings."

  def _getSerializer( self, settings, option ):

    try:
      node, key = settings.getNodeKeyByPath( option )
      defaults = node.getParentByLabel( SETTINGS_LABEL )
    except KeyError:
      return None

    return defaults.getSerializer( key )


  def cmd_set( self, world, option, *args ):

    u"""\
    Sets the given configuration option to the given value.

    Usage: %(cmd)s <option> <value>

    Example: %(cmd)s ui.view.font.name "Courier New"

    """

    args = " ".join( args )

    settings = QApplication.instance().core.config

    s = self._getSerializer( settings, option )

    if not s:
      world.info( u"Unknown configuration option: %s" % option )
      return

    args = s.deserialize( args )
    node, key = settings.getNodeKeyByPath( option )
    node[ key ] = args

    ## TODO: Factorize display between this, worldset, reset and worldreset.
    value = s.serialize( args )

    if value is None:
      value = u'None'

    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s set to value %s" % ( option, value ) )


  def cmd_worldset( self, world, option, *args ):

    u"""\
    Sets given configuration option to the given value, for this world only.

    Usage: %(cmd)s <option> <value>

    Example: %(cmd)s output_font_name "Courier New"

    """

    args = " ".join( args )

    t = world.conf.getType( option )

    if not t:
      world.info( u"Unknown configuration option: %s" % option )
      return

    args = t.from_string( args )
    world.conf[ option ] = args

    value = t.to_string( args )

    if value is None:
      value = u'None'

    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s set to value %s on world %s" \
                % ( option, value, world.title() ) )


  def cmd_reset( self, world, option ):

    u"""\
    Resets the given configuration option to its default value.

    Usage: %(cmd)s <option>

    Example: %(cmd)s output_font_name

    """

    t = world.conf.getType( option )

    if not t:
      world.info( u"Unknown configuration option: %s" % option )
      return

    config = QApplication.instance().core.config

    try:
      del config[ option ]

    except KeyError:
      pass

    value = t.to_string( config[ option ] )

    if value is None:
      value = u'None'

    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s reset to value %s" % ( option, value ) )


  def cmd_worldreset( self, world, option ):

    u"""\
    Resets the given configuration option for this world to its global value.

    Usage: %(cmd)s <option>

    Example: %(cmd)s output_font_name

    """

    t = world.conf.getType( option )

    if not t:
      world.info( u"Unknown configuration option: %s" % option )
      return

    try:
      del world.conf[ option ]

    except KeyError:
      pass

    value = t.to_string( world.conf[ option ] )

    if value is None:
      value = u'None'

    if ' ' in value:
      value = '"%s"' % value

    world.info( u"%s reset to value %s on world %s" \
                % ( option, value, world.title() ) )


  def cmd_options( self, world ):

    u"""\
    Lists all available configuration options.

    Usage: %(cmd)s

    """

    max_len = max( len( k ) for k in ALL_DESCS )

    output = u"Available configuration options:\n"

    for option, desc in sorted( ALL_DESCS.iteritems() ):
      output += option.ljust( max_len + 2 )
      output += desc
      output += '\n'

    world.info( output )


  def cmd_show( s, world, option=None ):

    u"""\
    Show the current configuration.

    Usage: %(cmd)s [<option> | all]

    By default, only the values differing from defaults are shown.
    If an optional option argument is given, list all values for that option
    (default, global, world.)

    If the optional argument 'all' is given, then all values for all options
    are listed.

    Examples:
        %(cmd)s output_font_name
        %(cmd)s all

    """

    worldconf  = world.conf
    globalconf = QApplication.instance().core.config
    defaults   = globalconf.parent

    ## 1/ Retrieve list of options to list, based on the argument given by the
    ## user:

    if option is not None:
      option = option.lower().strip()

    if option is None:  ## No argument given. Show non-default options.

      list_options = []

      for k in sorted( ALL_DESCS ):

        if worldconf.owns( k ) or globalconf.owns( k ):
          list_options.append( k )

      if not list_options:
        world.info( u"All the configuration options have default values." )
        return

    elif option == "all":
      list_options = sorted( ALL_DESCS )

    else:

      if defaults.getType( option ) is None:
        world.info( u"No such configuration option." )
        return

      list_options = [ option ]


    ## 2/ Format and display as a table:

    output = "Current configuration:\n"

    headers = ( u"Options", u"Defaults", u"Global", u"World" )

    columns = [ list_options ]

    for conf in ( defaults, globalconf, worldconf ):

      column = []

      for k in list_options:
        t = globalconf.getType( k )
        value = t.to_string( conf[ k ] ) if conf.owns( k ) else u"-"

        column.append( value if value else u"None" )

      columns.append( column )

    output += format_as_table( columns, headers )
    world.info( output )
