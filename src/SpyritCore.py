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
## SpyritCore.py
##
## Implements the 'brain' object that controls the primary subsystems in
## Spyrit.
##


from localqt import *

from Config          import Config
from MainWindow      import MainWindow
from SoundEngine     import SoundEngine
from WorldsManager   import WorldsManager
from TempResources   import TempResources
from TriggersManager import TriggersManager
from CommandRegistry import construct_command_registry

from Globals     import CMDCHAR
from ConfigPaths import CONFIG_FILE

from Messages   import messages


class SpyritCore:

  def __init__( s, config, worlds, commands, triggers, tmprc, sound ):

    s.config   = config
    s.worlds   = worlds
    s.commands = commands
    s.triggers = triggers
    s.tmprc    = tmprc
    s.sound    = sound
    s.mw       = None

    ## Set up a MOTD to properly welcome our user:

    MOTD = (
        u"Welcome to %s %s!" % ( config._app_name, config._app_version ),
        u"Type %shelp for help on available commands." % CMDCHAR
    )

    ## Note the use of iter(), so the MOTD is only displayed once for the whole
    ## application.
    s.motd = iter( MOTD )


  @QtCore.pyqtSlot()
  def atExit( s ):

    s.config.save( CONFIG_FILE )  ## TODO: Take this out of this file.
    s.tmprc.cleanup()


  def constructMainWindow( s ):

    if s.mw:
      return

    s.mw = MainWindow( s.config )
    s.mw.show()


  def openWorldByName( s, worldname ):

    world = s.worlds.lookupWorldByName( worldname )

    if world:
      s.openWorld( world )

    else:
      messages.warn( u"No such world: %s" % worldname )


  def openWorldByHostPort( s, host, port, ssl=False ):

    world = s.worlds.lookupWorldByHostPort( host, port )

    if world:
      s.openWorld( world )

    else:
      s.openWorld(
        s.worlds.newAnonymousWorld( host, port, ssl )
      )


  def openWorld( s, world ):

    s.mw.newWorldUI( world )
    world.connectToWorld()




def construct_spyrit_core( application ):

  config   = Config()
  worlds   = WorldsManager( config )
  tmprc    = TempResources()
  sound    = SoundEngine( tmprc )
  triggers = TriggersManager( config )  ## TODO: Take this out of this module.
  commands = construct_command_registry()

  core = SpyritCore(
           config=config,
           worlds=worlds,
           commands=commands,
           triggers=triggers,
           tmprc=tmprc,
           sound=sound,
         )

  application.aboutToQuit.connect( core.atExit )

  return core
