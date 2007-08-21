# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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
## Instanciates the configuration singleton.
##


from IniConfigBasket import IniConfigBasket
from ConfigPaths     import CONFIG_FILE
from Defaults        import defaults


config        = IniConfigBasket( CONFIG_FILE )
config.parent = defaults

if not config.hasDomain( config._worlds_section ):
  config.createDomain( config._worlds_section )

worldconfig = config.getDomain( config._worlds_section )
