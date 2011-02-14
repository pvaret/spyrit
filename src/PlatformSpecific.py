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
## PlatformSpecific.py
##
## Contains the class that encapsulate platform-dependant variations, i.e.
## configuration file paths and such.
##


import os
import sys

if os.name == 'posix':

  if sys.platform == 'darwin':
    from MacosSpecific import MacosSpecific as PlatformSpecific

  else:
    from PosixSpecific import PosixSpecific as PlatformSpecific

elif os.name == 'nt':
  from Win32Specific import Win32Specific as PlatformSpecific

else:
  raise NotImplementedError( "This program doesn't support your OS yet. "
                             "Sorry!" )


platformSpecific = PlatformSpecific()
