# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## SpyritCore.py
##
## Implements the 'brain' object that controls the primary subsystems in
## Spyrit.
##


from weakref import WeakSet

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot

from MainWindow      import MainWindow
from SoundEngine     import SoundEngine
from WorldsManager   import WorldsManager
from TempResources   import TempResources

from Globals         import CMDCHAR
from Messages        import messages
from SpyritSettings  import load_settings, save_settings
from TriggersManager import construct_triggersmanager
from CommandRegistry import construct_command_registry


class SpyritCore( QObject ):

  def __init__( self, settings, worlds, commands, triggers, tmprc, sound ):

    QObject.__init__( self )

    self.settings = settings
    self.worlds   = worlds
    self.commands = commands
    self.triggers = triggers
    self.tmprc    = tmprc
    self.sound    = sound
    self.mw       = None

    self.openworlds = WeakSet()

    ## Set up a MOTD to properly welcome our user:

    MOTD = (
        "Welcome to %s %s!" % ( settings._app._name, settings._app._version ),
        "Type %shelp for help on available commands." % CMDCHAR
    )

    ## Note the use of iter(), so the MOTD is only displayed once for the whole
    ## application.
    self.motd = iter( MOTD )


  @pyqtSlot()
  def atExit( self ):

    self.tmprc.cleanup()
    self.triggers.save( self.settings )
    save_settings( self.settings )


  def constructMainWindow( self ):

    if self.mw:
      return

    self.mw = MainWindow( self.settings )
    self.mw.show()


  def openWorldByName( self, worldname ):

    world = self.worlds.lookupWorldByName( worldname )

    if world:
      self.openWorld( world )

    else:
      messages.warn( "No such world: %s" % worldname )


  def openWorldByHostPort( self, host, port, ssl=False ):

    world = self.worlds.lookupWorldByHostPort( host, port )

    if world:
      self.openWorld( world )

    else:
      self.openWorld(
        self.worlds.newAnonymousWorld( host, port, ssl )
      )


  def openWorld( self, world ):

    self.openworlds.add( world )
    self.mw.newWorldUI( world )
    world.connectToWorld()




def construct_spyrit_core( application ):

  settings = load_settings()
  worlds   = WorldsManager( settings )
  tmprc    = TempResources()
  sound    = SoundEngine( tmprc )
  triggers = construct_triggersmanager( settings )
  commands = construct_command_registry()

  core = SpyritCore(
           settings=settings,
           worlds=worlds,
           commands=commands,
           triggers=triggers,
           tmprc=tmprc,
           sound=sound,
         )

  application.aboutToQuit.connect( core.atExit )

  return core
