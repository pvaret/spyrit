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


import os.path

from BaseCommand import BaseCommand
from Singletons  import singletons


class SoundCommand( BaseCommand ):

  u"Sound-related operations."

  def cmd_play( s, world, filename=":/sound/pop" ):

    u"""\
    Play a sound.

    Usage: %(cmd)s [<soundfile.wav>]

    If you omit the sound file name, a default 'pop' sound will be played.
    The purpose of this command is to test your sound setup.

    """

    filename = os.path.expanduser( filename )
    ok, msg = singletons.sound.play( filename )

    if not ok:
      world.info( msg )
