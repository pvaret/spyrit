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

from Singletons          import singletons
from DefaultSoundBackend import DefaultSoundBackend


class SoundEngine:


  def __init__( s ):

    s.backend      = None
    s.pollerthread = None

    s.pollForBackend()


  def pollForBackend( s ):

    ## We need a thread to poll backends, because in some cases, like with
    ## the QSound-based engine on Linux, the engine takes several seconds
    ## before returning a failure, thus blocking the UI in the meanwhile.
    ## Bummer.

    class EnginePollerThread( QtCore.QThread ):

      def run( thread ):

        for Backend in [ DefaultSoundBackend ]:

          b = Backend()

          if b.isAvailable():

            ## Variable assignment in Python is atomic, so it's okay to do
            ## this in a thread.

            s.backend = b
            break

    s.pollerthread = EnginePollerThread()
    s.pollerthread.start()


  def play( s, soundfile ):

    if not s.backend:
      return

    s.backend.play( singletons.tmprc.get( soundfile ) )


  def __del__( s ):

    if s.pollerthread:

      ## terminate() is rather rough, but if the thread still isn't done
      ## running by the time the engine gets destroyed, then there's a problem
      ## and aborting it is all we can do.

      s.pollerthread.terminate()
      s.pollerthread = None

    s.backend = None
