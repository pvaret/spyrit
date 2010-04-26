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
## SoundCommand.py
##
## Play sounds and manage sound engines.
##


from BaseCommand import BaseCommand
from Singletons  import singletons


class SoundCommand( BaseCommand ):

  u"Sound-related operations."

  def cmd_play( s, world, filename ):

    u"Play a sound."

    singletons.sound.play( filename )
