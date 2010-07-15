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
## SoundEngine.py
##
## Contains the SoundEngine class, our simple sound player. It tries to locate
## a backend that works on the user's platform and then uses it for playback.
##


from localqt import *

import os.path

from Singletons       import singletons
from QSoundBackend    import QSoundBackend
from PygameBackend    import PygameBackend
from PlatformSpecific import platformSpecific




class SoundBackendRegistry:

  SOUNDBACKENDS = {
    "qsound": QSoundBackend,
    "pygame": PygameBackend,
  }

  def __init__( s ):

    s.preferred_backends = platformSpecific.get_sound_backends()
    s.backend_cache = {}


  def pollForBackend( s ):

    for backend_name in s.preferred_backends:

      backend = s.lookupBackend( backend_name )

      if backend.isAvailable():
        return backend

    return None


  def lookupBackend( s, backend_name ):

    if backend_name not in s.backend_cache:
      s.backend_cache[ backend_name ] = s.SOUNDBACKENDS[ backend_name ]()

    return s.backend_cache[ backend_name ]


  def listBackends( s, also_list_unsupported=False ):

      if also_list_unsupported:
        backend_list = s.SOUNDBACKENDS.keys()
      else:
        backend_list = s.preferred_backends

      return [ s.lookupBackend( backend_name )
               for backend_name in backend_list ]


class SoundEngine:

  def __init__( s ):

    s.registry = SoundBackendRegistry()
    s.backend  = s.registry.pollForBackend()


  def play( s, soundfile ):

    if not s.backend:
      return False, u"No sound engine available."

    filename = singletons.tmprc.get( soundfile )

    if not os.path.exists( filename ):
      return False, u"%s: file not found." % soundfile

    if not os.path.isfile( filename ):
      return False, u"%s: not a valid file." % soundfile

    ## TODO: Check that filename is a valid WAV file.

    s.backend.play( filename )
    return True, None
