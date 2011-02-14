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
## Config.py
##
## Instantiates the configuration singleton.
##


from Defaults        import ALL_DEFAULTS, ALL_TYPES
from ConfigPaths     import CONFIG_FILE

from IniConfigBasket import IniConfigBasket
from TriggersManager import trigger_type_getter

config = None


def Config():

  global config

  if not config:

    type_getter_map = { ALL_DEFAULTS[ "matches_section" ]: trigger_type_getter }

    config = IniConfigBasket( ALL_DEFAULTS, ALL_TYPES )
    config.setTypeGetterForFutureSections( type_getter_map )
    config.load( CONFIG_FILE )

  return config
