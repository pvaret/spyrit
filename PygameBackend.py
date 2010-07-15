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
## PygameBackend.py
##
## Implements the pygame-based sound backend.
## This is mostly used on Linux, where it might be the most readily
## available backend.
##

HAS_PYGAME=False

try:
  import pygame
  HAS_PYGAME=True

except ImportError:
  ## Pygame not found. Bummer.
  pass


FREQUENCY = 44100  ## hz
SIZE      = -16    ## 16 bits, signed
CHANNELS  = 1      ## mono
BUFFER    = 1024   ## bytes


class PygameBackend:

  name = u"SDL"

  def __init__( s ):

    s.mixer = None


  def isAvailable( s ):

    if not HAS_PYGAME:
      return False

    s.mixer = pygame.mixer
    s.mixer.init( FREQUENCY, SIZE, CHANNELS, BUFFER )

    return True


  def play( s, soundfile ):

    if s.mixer:
      sound = s.mixer.Sound( soundfile )
      sound.play()


  def __del__( s ):

    if s.mixer:
      s.mixer.quit()
      s.mixer = None
