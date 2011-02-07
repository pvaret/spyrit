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
## NewWorldDialog.py
##
## This class holds the dialog that lets the user create a new world.
##

from localqt import *

from Utilities          import check_ssl_is_available

from PrettyOptionPanel  import ConfigMapper
from PrettyPanelHeader  import PrettyPanelHeader
from PrettyOptionDialog import PrettyOptionDialog


def NewWorldDialog( conf, parent=None ):

    header = PrettyPanelHeader( u"New world",
                                  QtGui.QPixmap( ":/icon/new_world" ) )

    mapper = ConfigMapper( conf )

    mapper.addGroup( u"World name", [
                       mapper.lineedit( "name" )
                     ] )

    mapper.addGroup( u"Connection parameters", [
                       mapper.lineedit( "host", u"&Server:" ),
                       mapper.spinbox(  "port", u"&Port:" ),
                     ] )

    if check_ssl_is_available():
      mapper.addGroup( u"Encryption", [
                         mapper.checkbox( "ssl", u"Use SSL &encryption"),
                       ] )

    dialog = PrettyOptionDialog( mapper,
                                 parent  = parent,
                                 header  = header,
                                 oklabel = u"Connect",
                                 title   = u"New world" )

    return dialog

