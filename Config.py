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
## Config.py
##
## Instanciates the configuration singleton.
##


from Defaults        import DEFAULTS, AUTOTYPES
from ConfigPaths     import CONFIG_FILE

from IniConfigBasket import IniConfigBasket

config = IniConfigBasket( CONFIG_FILE, DEFAULTS, AUTOTYPES )

def Config():

  global config
  return config
